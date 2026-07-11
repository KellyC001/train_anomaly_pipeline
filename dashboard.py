import json
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st

from src.database import load_recent_telemetry
from src.database import load_sensor_logs
from src.reporting import (
    build_daily_anomaly_summary,
    build_data_quality_report,
    build_model_health_report,
)
from src.report_store import load_latest_reports
from src.visualization import (
    build_anomaly_type_bar,
    build_door_anomaly_bar,
    build_door_metric_heatmap,
    build_feature_stats_bar,
    build_sensor_timeseries,
)

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="RailOps AI Operations Dashboard", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
    }
    .status-band {
        border: 1px solid #d7dde8;
        border-radius: 8px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .status-critical {
        border-left: 8px solid #c73535;
        background: #fff5f5;
    }
    .status-normal {
        border-left: 8px solid #1f7a4d;
        background: #f3fbf6;
    }
    .status-watch {
        border-left: 8px solid #c77d14;
        background: #fff8ed;
    }
    .section-note {
        color: #55606f;
        font-size: 0.94rem;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("RailOps AI Operations Dashboard")
st.caption("Train door anomaly monitoring, pipeline health, and diagnostic context.")


def parse_timestamp(value) -> datetime | None:
    if value is None:
        return None
    try:
        return pd.to_datetime(value, utc=True).to_pydatetime()
    except Exception:
        return None


def age_minutes(value) -> float | None:
    timestamp = parse_timestamp(value)
    if not timestamp:
        return None
    return max((datetime.now(timezone.utc) - timestamp).total_seconds() / 60, 0)


def format_age(value) -> str:
    minutes = age_minutes(value)
    if minutes is None:
        return "unknown"
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes:.0f} min ago"
    return f"{minutes / 60:.1f} hr ago"


def format_percent(value: float | int | None) -> str:
    return f"{float(value or 0) * 100:.1f}%"


def get_operational_status(summary: dict | None, quality: dict | None) -> tuple[str, str, str]:
    if not summary:
        return (
            "No Report Available",
            "Run `python orchestration.py all` to generate the latest operational reports.",
            "status-watch",
        )

    anomaly_count = int(summary.get("anomaly_count", 0))
    quality_status = str((quality or {}).get("status", "unknown")).lower()

    if quality_status not in {"pass", "no_data"}:
        return (
            "Data Quality Warning",
            "The monitoring checks found data quality issues. Review the Monitoring Health tab before acting on anomaly counts.",
            "status-watch",
        )

    if anomaly_count > 0:
        return (
            "Action Required",
            f"{anomaly_count} anomalies were detected in the latest reporting window.",
            "status-critical",
        )

    return (
        "Normal Operations",
        "No anomalies were detected in the latest reporting window.",
        "status-normal",
    )


def render_status_band(title: str, message: str, css_class: str) -> None:
    st.markdown(
        f"""
        <div class="status-band {css_class}">
            <div style="font-size: 1.15rem; font-weight: 700;">{title}</div>
            <div style="margin-top: 4px;">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_report_message() -> None:
    st.info("No report found yet. Run `python orchestration.py all` to generate reports.")


def render_raw_report(report: dict | None) -> None:
    if not report:
        return
    with st.expander("View raw JSON report"):
        st.code(json.dumps(report, indent=2, default=str), language="json")


def build_dataframe_from_mapping(mapping: dict, key_name: str, value_name: str) -> pd.DataFrame:
    if not mapping:
        return pd.DataFrame(columns=[key_name, value_name])
    return pd.DataFrame(mapping.items(), columns=[key_name, value_name])


scheduled_reports = load_latest_reports()
scheduled_summary_report = scheduled_reports["daily_anomaly_summary"]
scheduled_quality_report = scheduled_reports["data_quality_report"]
scheduled_health_report = scheduled_reports["model_health_report"]

try:
    telemetry_df = load_recent_telemetry(limit=25)
    live_window_df = load_sensor_logs(hours=24)
except Exception as error:
    telemetry_df = pd.DataFrame()
    live_window_df = pd.DataFrame()
    telemetry_error = str(error)
else:
    telemetry_error = None

if live_window_df.empty:
    summary_report = scheduled_summary_report
    quality_report = scheduled_quality_report
    health_report = scheduled_health_report
    report_mode = "Scheduled Prefect snapshot"
else:
    summary_report = build_daily_anomaly_summary(live_window_df, hours=24)
    quality_report = build_data_quality_report(live_window_df, hours=24)
    health_report = build_model_health_report(live_window_df, hours=24)
    report_mode = "Live PostgreSQL window"

command_tab, health_tab, telemetry_tab, diagnostics_tab = st.tabs(
    ["Command Center", "Monitoring Health", "Telemetry Explorer", "AI Diagnostics"]
)


with command_tab:
    status_title, status_message, status_class = get_operational_status(summary_report, quality_report)
    render_status_band(status_title, status_message, status_class)

    st.markdown('<div class="section-note">At-a-glance view for managers and operations leads.</div>', unsafe_allow_html=True)
    st.caption(f"Summary source: {report_mode}. Refresh the page to pull the latest database rows.")

    metric_cols = st.columns(5)
    metric_cols[0].metric("Anomalies", (summary_report or {}).get("anomaly_count", 0))
    metric_cols[1].metric("Anomaly Rate", format_percent((summary_report or {}).get("anomaly_rate", 0)))
    metric_cols[2].metric("Rows Checked", (summary_report or {}).get("row_count", 0))
    metric_cols[3].metric("Reporting Window", f"{(summary_report or {}).get('window_hours', 0)}h")
    metric_cols[4].metric("Report Freshness", format_age((summary_report or {}).get("generated_at")))

    if not summary_report:
        render_empty_report_message()
    else:
        left, right = st.columns([1.15, 0.85])

        with left:
            st.subheader("Latest Anomaly Evidence")
            latest_anomalies = summary_report.get("latest_anomalies", [])
            if latest_anomalies:
                anomaly_df = pd.DataFrame(latest_anomalies)
                display_columns = [
                    "timestamp",
                    "door_id",
                    "anomaly_type",
                    "motor_current",
                    "vibration",
                    "voltage",
                    "cycle_duration",
                ]
                st.dataframe(anomaly_df[display_columns], width="stretch", hide_index=True)
            else:
                st.success("No anomaly records in the latest reporting window.")

        with right:
            st.subheader("Where To Look First")
            st.plotly_chart(
                build_door_anomaly_bar(summary_report),
                width="stretch",
                key="command_door_anomaly_bar",
            )
            st.plotly_chart(
                build_anomaly_type_bar(summary_report),
                width="stretch",
                key="command_anomaly_type_bar",
            )

    st.divider()
    st.subheader("Live Signal")
    if telemetry_error:
        st.warning("Live telemetry is unavailable.")
        with st.expander("Connection details"):
            st.code(telemetry_error)
    elif telemetry_df.empty:
        st.info("No live telemetry rows found yet.")
    else:
        latest_timestamp = telemetry_df["timestamp"].max()
        signal_cols = st.columns(4)
        signal_cols[0].metric("Latest Reading", format_age(latest_timestamp))
        signal_cols[1].metric("Rows Loaded", len(telemetry_df))
        signal_cols[2].metric("Latest Door", telemetry_df.iloc[0]["door_id"])
        signal_cols[3].metric("Latest Flag", "Anomaly" if telemetry_df.iloc[0]["anomaly_flag"] == 1 else "Normal")

        st.plotly_chart(
            build_sensor_timeseries(telemetry_df, "motor_current"),
            width="stretch",
            key="command_motor_current_timeseries",
        )
        st.plotly_chart(
            build_door_metric_heatmap(telemetry_df),
            width="stretch",
            key="command_door_metric_heatmap",
        )


with health_tab:
    st.header("Monitoring Health")
    st.markdown(
        '<div class="section-note">Checks whether the dashboard data is complete, fresh, and trustworthy.</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Health metrics source: {report_mode}. Scheduled Prefect reports remain available as audit snapshots.")

    quality_status = str((quality_report or {}).get("status", "missing")).upper()
    total_issues = (quality_report or {}).get("total_issues", "n/a")
    health_cols = st.columns(5)
    health_cols[0].metric("Data Quality", quality_status)
    health_cols[1].metric("Quality Issues", total_issues)
    health_cols[2].metric("Duplicate Rows", (quality_report or {}).get("duplicate_count", "n/a"))
    health_cols[3].metric("Quality Report Age", format_age((quality_report or {}).get("generated_at")))
    health_cols[4].metric("Model Report Age", format_age((health_report or {}).get("generated_at")))

    if not quality_report:
        render_empty_report_message()
    else:
        left, right = st.columns(2)
        with left:
            st.subheader("Completeness Checks")
            st.dataframe(
                build_dataframe_from_mapping(quality_report.get("null_counts", {}), "Column", "Missing Values"),
                width="stretch",
                hide_index=True,
            )

            missing_columns = quality_report.get("missing_columns", [])
            if missing_columns:
                st.warning(f"Missing expected columns: {', '.join(missing_columns)}")
            else:
                st.success("All expected columns are present.")

        with right:
            st.subheader("Validity Checks")
            st.dataframe(
                build_dataframe_from_mapping(quality_report.get("invalid_ranges", {}), "Check", "Failures"),
                width="stretch",
                hide_index=True,
            )

            if int(quality_report.get("total_issues", 0)) == 0:
                st.success("No missing, duplicate, or invalid data found.")
            else:
                st.warning("Data quality issues found. Review the failed checks before using anomaly metrics.")

        render_raw_report(quality_report)

        with st.expander("Latest scheduled Prefect data quality snapshot"):
            if scheduled_quality_report:
                st.code(json.dumps(scheduled_quality_report, indent=2, default=str), language="json")
            else:
                st.info("No scheduled Prefect data quality snapshot found yet.")

    st.divider()
    st.subheader("Model Monitoring")
    if not health_report:
        render_empty_report_message()
    else:
        model_cols = st.columns(4)
        model_cols[0].metric("Rows Scored", health_report.get("row_count", 0))
        model_cols[1].metric("Anomalies", health_report.get("anomaly_count", 0))
        model_cols[2].metric("Anomaly Rate", format_percent(health_report.get("anomaly_rate", 0)))
        model_cols[3].metric("Window", f"{health_report.get('window_hours', 0)}h")

        feature_stats = health_report.get("feature_stats", {})
        if feature_stats:
            feature_df = pd.DataFrame.from_dict(feature_stats, orient="index").reset_index()
            feature_df = feature_df.rename(columns={"index": "feature"})
            st.plotly_chart(
                build_feature_stats_bar(health_report),
                width="stretch",
                key="health_feature_stats_bar",
            )
            st.dataframe(feature_df, width="stretch", hide_index=True)

        thresholds = health_report.get("rule_thresholds", {})
        if thresholds:
            st.markdown("Rule-based safety thresholds")
            st.dataframe(
                build_dataframe_from_mapping(thresholds, "Threshold", "Value"),
                width="stretch",
                hide_index=True,
            )

        render_raw_report(health_report)

        with st.expander("Latest scheduled Prefect model health snapshot"):
            if scheduled_health_report:
                st.code(json.dumps(scheduled_health_report, indent=2, default=str), language="json")
            else:
                st.info("No scheduled Prefect model health snapshot found yet.")


with telemetry_tab:
    st.header("Telemetry Explorer")
    st.markdown(
        '<div class="section-note">Detailed sensor readings for analysts who need to inspect the underlying records.</div>',
        unsafe_allow_html=True,
    )

    if telemetry_error:
        st.warning("Live telemetry is unavailable.")
        with st.expander("Connection details"):
            st.code(telemetry_error)
    elif telemetry_df.empty:
        st.info("No telemetry rows found yet.")
    else:
        def anomaly_styler(row):
            return ["background-color: #ffeeee" if row["anomaly_flag"] == 1 else "" for _ in row]

        st.dataframe(telemetry_df.style.apply(anomaly_styler, axis=1), width="stretch")

        st.subheader("Sensor Trends")
        metric = st.selectbox(
            "Sensor metric",
            ["motor_current", "vibration", "voltage", "cycle_duration"],
            format_func=lambda value: value.replace("_", " ").title(),
        )
        st.plotly_chart(
            build_sensor_timeseries(telemetry_df, metric),
            width="stretch",
            key=f"telemetry_{metric}_timeseries",
        )
        st.plotly_chart(
            build_door_metric_heatmap(telemetry_df),
            width="stretch",
            key="telemetry_door_metric_heatmap",
        )


with diagnostics_tab:
    st.header("AI Diagnostics")
    st.markdown(
        '<div class="section-note">Diagnostic API tools that a future LLM agent can call for explanation and recommended action.</div>',
        unsafe_allow_html=True,
    )

    target_door = st.selectbox("Door to inspect", ["Door-A1", "Door-A2", "Door-B1", "Door-B2"])
    execute_agent = st.button("Run Diagnostic Tool Check")

    if execute_agent:
        with st.spinner("Calling diagnostic API tools..."):
            try:
                fault_response = requests.get(
                    f"{FASTAPI_BASE_URL}/tools/query_recent_faults",
                    params={"door_id": target_door},
                    timeout=5,
                )
                fault_response.raise_for_status()
                fault_context = fault_response.json()

                notes_response = requests.get(
                    f"{FASTAPI_BASE_URL}/tools/fetch_engineering_logs",
                    params={"door_id": target_door},
                    timeout=5,
                )
                notes_response.raise_for_status()
                maintenance_context = notes_response.json()

                st.subheader("Tool Outputs")
                left, right = st.columns(2)
                with left:
                    st.markdown("Recent database faults")
                    st.json(fault_context)
                with right:
                    st.markdown("Maintenance context")
                    st.json(maintenance_context)

                st.subheader("Current Interpretation")
                if fault_context:
                    st.warning(
                        "This API layer is ready for an LLM agent. A future agent can combine recent faults "
                        "with maintenance notes and produce a structured incident report."
                    )
                else:
                    st.success("No recent database faults were returned for this door.")
            except Exception as error:
                st.error("Diagnostic API is unavailable. Confirm `mcp_server.py` is running on port 8000.")
                with st.expander("Connection details"):
                    st.code(str(error))
