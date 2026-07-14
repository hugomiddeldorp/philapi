CREATE TABLE countries (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE philosophers (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    date_of_birth TIMESTAMP,
    date_of_death TIMESTAMP,
    country_id INTEGER REFERENCES countries(id)
);

CREATE TABLE schools (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE school_memberships (
    philosopher_id INTEGER REFERENCES philosophers(id),
    school_id INTEGER REFERENCES schools(id),
    PRIMARY KEY (philosopher_id, school_id)
);

CREATE TABLE school_influences (
    school_id INTEGER REFERENCES schools(id),
    influence_by INTEGER REFERENCES schools(id),
    PRIMARY KEY (school_id, influence_by),
    CHECK (school_id <> influence_by)
);

CREATE TABLE relationships (
    teacher_id INTEGER REFERENCES philosophers(id),
    student_id INTEGER REFERENCES philosophers(id),
    PRIMARY KEY (teacher_id, student_id),
    CHECK (teacher_id <> student_id)
);

CREATE TABLE works (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL,
    author INTEGER REFERENCES philosophers(id),
    published_year INTEGER
);

CREATE TABLE subjects (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE work_subjects (
    work_id INTEGER REFERENCES works(id),
    subject_id INTEGER REFERENCES subjects(id),
    PRIMARY KEY (work_id, subject_id)
);
