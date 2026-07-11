import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


@dataclass(frozen=True)
class Settings:
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "train-doors")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    postgres_db: str = os.getenv("POSTGRES_DB", "traindb")
    postgres_user: str = os.getenv("POSTGRES_USER", "user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "change_me")
    dashboard_alert_webhook: str = os.getenv(
        "DASHBOARD_ALERT_WEBHOOK",
        "http://localhost:8501/alert_webhook",
    )
    reports_dir: str = os.getenv("REPORTS_DIR", "reports")


settings = Settings()
