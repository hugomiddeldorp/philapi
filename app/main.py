from fastapi import FastAPI

app = FastAPI(title="PhilAPI")


@app.get("/health")
def health_check():
    return {"status": "ok"}
