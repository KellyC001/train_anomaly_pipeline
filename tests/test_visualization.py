import pandas as pd
import plotly.graph_objects as go

from src.visualization import (
    build_anomaly_type_bar,
    build_door_anomaly_bar,
    build_door_metric_heatmap,
    build_feature_stats_bar,
    build_sensor_timeseries,
)


def sample_telemetry() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "timestamp": "2026-07-11T02:34:18Z",
                "door_id": "Door-A1",
                "motor_current": 2.2,
                "vibration": 0.3,
                "voltage": 24.4,
                "cycle_duration": 3.5,
                "anomaly_flag": 0,
            },
            {
                "timestamp": "2026-07-11T02:35:18Z",
                "door_id": "Door-A1",
                "motor_current": 7.9,
                "vibration": 0.4,
                "voltage": 24.2,
                "cycle_duration": 3.7,
                "anomaly_flag": 1,
            },
        ]
    )


def test_build_sensor_timeseries_returns_plotly_figure():
    fig = build_sensor_timeseries(sample_telemetry(), "motor_current")

    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2


def test_build_door_metric_heatmap_returns_plotly_figure():
    fig = build_door_metric_heatmap(sample_telemetry())

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1


def test_summary_charts_return_plotly_figures():
    summary = {
        "most_affected_doors": {"Door-A1": 2},
        "anomaly_types": {"Motor Obstruction Fault": 2},
    }

    assert isinstance(build_door_anomaly_bar(summary), go.Figure)
    assert isinstance(build_anomaly_type_bar(summary), go.Figure)


def test_feature_stats_chart_returns_plotly_figure():
    health = {
        "feature_stats": {
            "motor_current": {"mean": 3.2, "max": 7.9},
            "voltage": {"mean": 23.0, "max": 24.8},
        }
    }

    fig = build_feature_stats_bar(health)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2
