import pandas as pd

from src.reporting import (
    build_daily_anomaly_summary,
    build_data_quality_report,
    build_model_health_report,
    write_report,
)


def sample_logs() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": 1,
                "timestamp": "2026-07-10T00:00:00",
                "door_id": "Door-A1",
                "cycle_state": "CLOSING",
                "motor_current": 2.2,
                "vibration": 0.35,
                "voltage": 24.4,
                "cycle_duration": 3.5,
                "anomaly_flag": 0,
                "anomaly_type": "Normal Cycle",
            },
            {
                "id": 2,
                "timestamp": "2026-07-10T00:01:00",
                "door_id": "Door-A1",
                "cycle_state": "CLOSING",
                "motor_current": 7.2,
                "vibration": 0.4,
                "voltage": 24.1,
                "cycle_duration": 3.7,
                "anomaly_flag": 1,
                "anomaly_type": "Motor Obstruction Fault",
            },
        ]
    )


def test_daily_anomaly_summary_counts_anomalies():
    report = build_daily_anomaly_summary(sample_logs())

    assert report["row_count"] == 2
    assert report["anomaly_count"] == 1
    assert report["anomaly_rate"] == 0.5
    assert report["most_affected_doors"] == {"Door-A1": 1}


def test_data_quality_report_passes_clean_data():
    report = build_data_quality_report(sample_logs())

    assert report["status"] == "pass"
    assert report["total_issues"] == 0


def test_model_health_report_includes_feature_stats():
    report = build_model_health_report(sample_logs())

    assert report["anomaly_rate"] == 0.5
    assert "motor_current" in report["feature_stats"]
    assert report["feature_stats"]["motor_current"]["max"] == 7.2


def test_write_report_creates_json_file(tmp_path):
    report = build_daily_anomaly_summary(sample_logs())

    report_path = write_report(report, output_dir=tmp_path)

    assert report_path.exists()
    assert report_path.name.endswith("_daily_anomaly_summary.json")
