import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.anomaly_model import FEATURE_COLUMNS
from src.config import settings


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_empty_report(report_type: str, hours: int) -> dict:
    return {
        "report_type": report_type,
        "generated_at": _now_iso(),
        "window_hours": hours,
        "row_count": 0,
        "status": "no_data",
    }


def build_daily_anomaly_summary(df: pd.DataFrame, hours: int = 24) -> dict:
    if df.empty:
        return build_empty_report("daily_anomaly_summary", hours)

    anomaly_df = df[df["anomaly_flag"] == 1]
    anomaly_count = int(len(anomaly_df))
    row_count = int(len(df))

    return {
        "report_type": "daily_anomaly_summary",
        "generated_at": _now_iso(),
        "window_hours": hours,
        "row_count": row_count,
        "anomaly_count": anomaly_count,
        "anomaly_rate": round(anomaly_count / row_count, 4),
        "most_affected_doors": anomaly_df["door_id"].value_counts().head(5).to_dict(),
        "anomaly_types": anomaly_df["anomaly_type"].value_counts().to_dict(),
        "latest_anomalies": anomaly_df.head(10).to_dict(orient="records"),
    }


def build_data_quality_report(df: pd.DataFrame, hours: int = 24) -> dict:
    if df.empty:
        return build_empty_report("data_quality_report", hours)

    expected_columns = {
        "id",
        "timestamp",
        "door_id",
        "cycle_state",
        "motor_current",
        "vibration",
        "voltage",
        "cycle_duration",
        "anomaly_flag",
        "anomaly_type",
    }
    missing_columns = sorted(expected_columns - set(df.columns))
    null_counts = df.isna().sum().astype(int).to_dict()
    duplicate_count = int(df.duplicated(subset=["timestamp", "door_id"]).sum())
    invalid_ranges = {
        "motor_current_below_zero": int((df["motor_current"] < 0).sum()),
        "vibration_below_zero": int((df["vibration"] < 0).sum()),
        "voltage_below_zero": int((df["voltage"] < 0).sum()),
        "cycle_duration_below_zero": int((df["cycle_duration"] < 0).sum()),
        "invalid_anomaly_flag": int((~df["anomaly_flag"].isin([0, 1])).sum()),
    }
    total_issues = (
        len(missing_columns)
        + sum(null_counts.values())
        + duplicate_count
        + sum(invalid_ranges.values())
    )

    return {
        "report_type": "data_quality_report",
        "generated_at": _now_iso(),
        "window_hours": hours,
        "row_count": int(len(df)),
        "status": "pass" if total_issues == 0 else "warn",
        "missing_columns": missing_columns,
        "null_counts": null_counts,
        "duplicate_count": duplicate_count,
        "invalid_ranges": invalid_ranges,
        "total_issues": int(total_issues),
    }


def build_model_health_report(df: pd.DataFrame, hours: int = 24) -> dict:
    if df.empty:
        return build_empty_report("model_health_report", hours)

    anomaly_count = int((df["anomaly_flag"] == 1).sum())
    row_count = int(len(df))
    feature_stats = {}
    for column in FEATURE_COLUMNS:
        feature_stats[column] = {
            "mean": round(float(df[column].mean()), 4),
            "min": round(float(df[column].min()), 4),
            "max": round(float(df[column].max()), 4),
            "std": round(float(df[column].std(ddof=0)), 4),
        }

    return {
        "report_type": "model_health_report",
        "generated_at": _now_iso(),
        "window_hours": hours,
        "row_count": row_count,
        "anomaly_count": anomaly_count,
        "anomaly_rate": round(anomaly_count / row_count, 4),
        "feature_stats": feature_stats,
        "rule_thresholds": {
            "motor_current_high": 4.5,
            "vibration_high": 1.2,
            "voltage_low": 19.5,
            "cycle_duration_high": 5.5,
        },
    }


def write_report(report: dict, output_dir: str | Path | None = None) -> Path:
    output_path = Path(output_dir or settings.reports_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = output_path / f"{timestamp}_{report['report_type']}.json"
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report_path
