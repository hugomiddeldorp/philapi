# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "sparqlwrapper>=2.0.0",
# ]
# ///
"""
This script is used to gather the data for the database using WikiData. It
produces five .JSON files containing information about philosophers, their
works, their schools and the relationships between them.

To run from the root of the repository: `uv run scripts/sparql.py`
"""

import json
from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT_URL = "https://query.wikidata.org/sparql"

PHIL_QUERY = """
SELECT ?philosopher ?philosopherLabel 
       (SAMPLE(?b) AS ?birth)
       (SAMPLE(?d) AS ?death)
       (SAMPLE(?countryLabel) AS ?country)
       ?sitelinks
WHERE {
  {
    SELECT ?philosopher ?sitelinks WHERE {
      ?philosopher wdt:P31 wd:Q5 ;            # instance of human
                   wdt:P101 wd:Q5891 ;         # field of work: philosophy
                   wikibase:sitelinks ?sitelinks .
    }
    ORDER BY DESC(?sitelinks)
    LIMIT 200
  }
  OPTIONAL { ?philosopher wdt:P569 ?b. }
  OPTIONAL { ?philosopher wdt:P570 ?d. }
  OPTIONAL {
  ?philosopher wdt:P19 ?birthPlace .
  ?birthPlace rdfs:label ?birthPlaceLabel . FILTER(LANG(?birthPlaceLabel) = "en")
  OPTIONAL {
    ?birthPlace wdt:P131* ?adminArea .
    ?adminArea wdt:P31 wd:Q6256 .          # instance of: country
    ?adminArea rdfs:label ?countryLabel . FILTER(LANG(?countryLabel) = "en")
  }
}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?philosopher ?philosopherLabel ?sitelinks
ORDER BY DESC(?sitelinks)
"""

STUDENT_QUERY = """
SELECT ?philosopher ?philosopherLabel ?student ?studentLabel
WHERE {
  VALUES ?philosopher { %s }

  ?philosopher wdt:P802 ?student .

  ?student rdfs:label ?studentLabel . FILTER(LANG(?studentLabel) = "en")

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?philosopherLabel
"""

WORKS_QUERY = """
SELECT ?philosopher ?philosopherLabel ?work ?workLabel ?pubYear ?genreLabel ?subjectLabel
WHERE {
  VALUES ?philosopher { %s }

  ?philosopher wdt:P800 ?work .

  ?work rdfs:label ?workLabel . FILTER(LANG(?workLabel) = "en")

  OPTIONAL {
    ?work p:P577 ?pubStatement . ?pubStatement ps:P577 ?pub ;
          wikibase:rank wikibase:PreferredRank .
    BIND(YEAR(?pub) AS ?pubYear)
  }
  OPTIONAL {
    ?work wdt:P571 ?inception .
    BIND(YEAR(?inception) AS ?pubYear)
  }
  OPTIONAL {
    ?work wdt:P136 ?genre .
    ?genre rdfs:label ?genreLabel . FILTER(LANG(?genreLabel) = "en")
  }
  OPTIONAL {
    ?work wdt:P921 ?subject .
    ?subject rdfs:label ?subjectLabel . FILTER(LANG(?subjectLabel) = "en")
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?philosopherLabel
"""

MOVEMENT_QUERY = """
SELECT ?philosopher ?philosopherLabel ?school ?schoolLabel ?schoolDescription
WHERE {
  VALUES ?philosopher { %s }
  ?philosopher wdt:P135 ?school .
  ?school rdfs:label ?schoolLabel . FILTER(LANG(?schoolLabel) = "en")
  OPTIONAL {
    ?school schema:description ?schoolDescription . FILTER(LANG(?schoolDescription) = "en")
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?philosopherLabel
"""

MOVEMENT_INFLUENCE_QUERY = """
SELECT ?school ?schoolLabel ?influencedBy ?influencedByLabel
WHERE {
  VALUES ?school { %s }

  ?school wdt:P737 ?influencedBy .

  ?influencedBy rdfs:label ?influencedByLabel . FILTER(LANG(?influencedByLabel) = "en")

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ?schoolLabel
"""


def populate_query(query: str, l: list, label: str) -> str:
    """
    Some queries required populating before sending off, for example populating
    the philosophers to get their students.
    """
    qids = []
    for item in l:
        qids.append(item[label]["value"].split("/")[-1])
    qids_string = " ".join(f"wd:{qid}" for qid in qids)
    return query % qids_string


def get_results(endpoint_url: str, query: str) -> dict:
    """
    SPARQL wrapper to make the query
    """
    user_agent = "PhilAPI-Scraper Python3.13 (hugomiddeldorp@gmail.com)"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


print("Getting philosophers")
r = get_results(ENDPOINT_URL, PHIL_QUERY)
philosophers = r["results"]["bindings"]

print("Getting their students")
r = get_results(
    ENDPOINT_URL, populate_query(STUDENT_QUERY, philosophers, "philosopher")
)
students = r["results"]["bindings"]

print("Getting their works")
r = get_results(ENDPOINT_URL, populate_query(WORKS_QUERY, philosophers, "philosopher"))
works = r["results"]["bindings"]

print("Getting their schools")
r = get_results(
    ENDPOINT_URL, populate_query(MOVEMENT_QUERY, philosophers, "philosopher")
)
movements = r["results"]["bindings"]

print("Getting influences to their schools")
r = get_results(
    ENDPOINT_URL, populate_query(MOVEMENT_INFLUENCE_QUERY, movements, "school")
)
movements_influence = r["results"]["bindings"]

# Write files in the root of the repository
files_map = {
    "philosophers": philosophers,
    "students": students,
    "works": works,
    "movements": movements,
    "movements_influence": movements_influence,
}
for k, v in files_map.items():
    with open(f"{k}.json", "w", encoding="utf-8") as f:
        json.dump(v, f, indent=2)
