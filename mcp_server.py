from fastapi import FastAPI
import uvicorn

from src.database import query_recent_faults as query_recent_faults_from_db

app = FastAPI(title="RailOps AI Diagnostic Tool Gateway")


@app.get("/tools/query_recent_faults")
def query_recent_faults(door_id: str):
    """Expose recent PostgreSQL anomalies for the requested train door."""
    try:
        return query_recent_faults_from_db(door_id)
    except Exception as error:
        return {"status": "error", "message": str(error)}


@app.get("/tools/fetch_engineering_logs")
def fetch_engineering_logs(door_id: str):
    """Return simulated maintenance notes for RAG-style diagnostic context."""
    return {
        "door_id": door_id,
        "historical_notes": (
            "Structural inspection warning: guide rail housing for Door-A1 "
            "shows slight compression warping (+1.5mm) after rush-hour cycles."
        ),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
