# mcp_server.py
from fastapi import FastAPI
import os
import psycopg2
import uvicorn

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = FastAPI(title="LTA-Kafka-Postgres-MCP-Gateway")

def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"]
    )

@app.get("/tools/query_recent_faults")
def query_recent_faults(door_id: str):
    """Exposes recent PostgreSQL database anomalies for the requested train asset asset door."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT timestamp, motor_current, vibration, voltage, cycle_duration, anomaly_type 
            FROM sensor_logs 
            WHERE door_id = %s AND anomaly_flag = 1 
            ORDER BY timestamp DESC LIMIT 3
        """, (door_id,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        conn.close()

@app.get("/tools/fetch_engineering_logs")
def fetch_engineering_logs(door_id: str):
    """Retrieves plain-text historic maintenance diagnostic records for structural reasoning context."""
    # Simulating standard infrastructure text log assets
    return {
        "door_id": door_id,
        "historical_notes": "Structural inspection warning: Guide rail housing for Door-A1 exhibits slight physical compression warping (+1.5mm) after extensive rush-hour operational strain cycles."
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)