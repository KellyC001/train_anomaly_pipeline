import argparse
import os

os.environ.setdefault("PREFECT_HOME", ".prefect")

from prefect import flow, serve, task

from src.database import ensure_schema, get_db_connection, load_sensor_logs
from src.reporting import (
    build_daily_anomaly_summary,
    build_data_quality_report,
    build_model_health_report,
    write_report,
)


@task(retries=2, retry_delay_seconds=10)
def ensure_database_schema() -> None:
    conn = get_db_connection()
    try:
        ensure_schema(conn)
    finally:
        conn.close()


@task(retries=2, retry_delay_seconds=10)
def fetch_recent_sensor_logs(hours: int):
    return load_sensor_logs(hours=hours)


@task
def create_daily_anomaly_summary(df, hours: int) -> dict:
    return build_daily_anomaly_summary(df, hours=hours)


@task
def create_data_quality_report(df, hours: int) -> dict:
    return build_data_quality_report(df, hours=hours)


@task
def create_model_health_report(df, hours: int) -> dict:
    return build_model_health_report(df, hours=hours)


@task
def persist_report(report: dict) -> str:
    return str(write_report(report))


@flow(name="daily-anomaly-summary")
def daily_anomaly_summary_flow(hours: int = 24) -> str:
    ensure_database_schema()
    df = fetch_recent_sensor_logs(hours)
    report = create_daily_anomaly_summary(df, hours)
    return persist_report(report)


@flow(name="data-quality-check")
def data_quality_check_flow(hours: int = 24) -> str:
    ensure_database_schema()
    df = fetch_recent_sensor_logs(hours)
    report = create_data_quality_report(df, hours)
    return persist_report(report)


@flow(name="model-health-report")
def model_health_report_flow(hours: int = 24) -> str:
    ensure_database_schema()
    df = fetch_recent_sensor_logs(hours)
    report = create_model_health_report(df, hours)
    return persist_report(report)


@flow(name="railops-daily-operations")
def railops_daily_operations_flow(hours: int = 24) -> dict:
    ensure_database_schema()
    df = fetch_recent_sensor_logs(hours)

    anomaly_report = create_daily_anomaly_summary(df, hours)
    quality_report = create_data_quality_report(df, hours)
    health_report = create_model_health_report(df, hours)

    return {
        "daily_anomaly_summary": persist_report(anomaly_report),
        "data_quality_report": persist_report(quality_report),
        "model_health_report": persist_report(health_report),
    }


def serve_scheduled_flows() -> None:
    serve(
        daily_anomaly_summary_flow.to_deployment(
            name="daily-anomaly-summary-deployment",
            cron="0 8 * * *",
            parameters={"hours": 24},
        ),
        data_quality_check_flow.to_deployment(
            name="data-quality-check-deployment",
            cron="0 * * * *",
            parameters={"hours": 24},
        ),
        model_health_report_flow.to_deployment(
            name="model-health-report-deployment",
            cron="30 8 * * *",
            parameters={"hours": 24},
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RailOps AI Prefect flows.")
    parser.add_argument(
        "flow",
        choices=["daily", "quality", "health", "all", "serve"],
        help="Which flow to run.",
    )
    parser.add_argument("--hours", type=int, default=24, help="Lookback window in hours.")
    args = parser.parse_args()

    if args.flow == "daily":
        print(daily_anomaly_summary_flow(hours=args.hours))
    elif args.flow == "quality":
        print(data_quality_check_flow(hours=args.hours))
    elif args.flow == "health":
        print(model_health_report_flow(hours=args.hours))
    elif args.flow == "all":
        print(railops_daily_operations_flow(hours=args.hours))
    elif args.flow == "serve":
        serve_scheduled_flows()


if __name__ == "__main__":
    main()
