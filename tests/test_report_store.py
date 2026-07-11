import json

from src.report_store import load_latest_report, load_latest_reports


def test_load_latest_report_returns_newest_matching_report(tmp_path):
    older = tmp_path / "20260710T000000Z_model_health_report.json"
    newer = tmp_path / "20260710T010000Z_model_health_report.json"
    older.write_text(json.dumps({"report_type": "model_health_report", "row_count": 1}))
    newer.write_text(json.dumps({"report_type": "model_health_report", "row_count": 2}))

    report = load_latest_report("model_health_report", reports_dir=tmp_path)

    assert report["row_count"] == 2


def test_load_latest_reports_returns_none_when_missing(tmp_path):
    reports = load_latest_reports(reports_dir=tmp_path)

    assert reports["daily_anomaly_summary"] is None
    assert reports["data_quality_report"] is None
    assert reports["model_health_report"] is None
