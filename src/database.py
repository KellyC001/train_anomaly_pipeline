import psycopg2
import pandas as pd

from src.config import settings


def get_db_connection():
    return psycopg2.connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
    )


def ensure_schema(conn) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sensor_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                door_id VARCHAR(50),
                cycle_state VARCHAR(50),
                motor_current REAL,
                vibration REAL,
                voltage REAL,
                cycle_duration REAL,
                anomaly_flag INTEGER,
                anomaly_type VARCHAR(100)
            );
            """
        )
    conn.commit()


def insert_sensor_log(conn, telemetry: dict, anomaly_flag: int, anomaly_type: str) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sensor_logs (
                timestamp,
                door_id,
                cycle_state,
                motor_current,
                vibration,
                voltage,
                cycle_duration,
                anomaly_flag,
                anomaly_type
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                telemetry["timestamp"],
                telemetry["door_id"],
                telemetry["cycle_state"],
                telemetry["motor_current"],
                telemetry["vibration"],
                telemetry["voltage"],
                telemetry["cycle_duration"],
                anomaly_flag,
                anomaly_type,
            ),
        )
    conn.commit()


def query_recent_faults(door_id: str, limit: int = 3) -> list[dict]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    timestamp,
                    motor_current,
                    vibration,
                    voltage,
                    cycle_duration,
                    anomaly_type
                FROM sensor_logs
                WHERE door_id = %s AND anomaly_flag = 1
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (door_id, limit),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()


def load_sensor_logs(hours: int = 24) -> pd.DataFrame:
    """Load recent sensor logs into a DataFrame for reporting and orchestration."""
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    timestamp,
                    door_id,
                    cycle_state,
                    motor_current,
                    vibration,
                    voltage,
                    cycle_duration,
                    anomaly_flag,
                    anomaly_type
                FROM sensor_logs
                WHERE timestamp >= NOW() - (%s || ' hours')::interval
                ORDER BY timestamp DESC
                """,
                (hours,),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()


def load_recent_telemetry(limit: int = 12) -> pd.DataFrame:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    timestamp,
                    door_id,
                    motor_current,
                    vibration,
                    voltage,
                    cycle_duration,
                    anomaly_flag
                FROM sensor_logs
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return pd.DataFrame(rows, columns=columns)
    finally:
        conn.close()
