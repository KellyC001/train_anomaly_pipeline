import json
from pathlib import Path

from src.config import settings


REPORT_LABELS = {
    "daily_anomaly_summary": "Daily Anomaly Summary",
    "data_quality_report": "Data Quality Report",
    "model_health_report": "Model Health Report",
}


def list_report_files(report_type: str | None = None, reports_dir: str | Path | None = None) -> list[Path]:
    base_path = Path(reports_dir or settings.reports_dir)
    if not base_path.exists():
        return []

    pattern = f"*_{report_type}.json" if report_type else "*.json"
    return sorted(base_path.glob(pattern), reverse=True)


def load_latest_report(report_type: str, reports_dir: str | Path | None = None) -> dict | None:
    report_files = list_report_files(report_type, reports_dir=reports_dir)
    if not report_files:
        return None

    return json.loads(report_files[0].read_text(encoding="utf-8"))


def load_latest_reports(reports_dir: str | Path | None = None) -> dict[str, dict | None]:
    return {
        report_type: load_latest_report(report_type, reports_dir=reports_dir)
        for report_type in REPORT_LABELS
    }
