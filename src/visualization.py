import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SENSOR_THRESHOLDS = {
    "motor_current": {"label": "Motor current high", "value": 4.5, "direction": "above"},
    "vibration": {"label": "Vibration high", "value": 1.2, "direction": "above"},
    "voltage": {"label": "Voltage low", "value": 19.5, "direction": "below"},
    "cycle_duration": {"label": "Cycle duration high", "value": 5.5, "direction": "above"},
}

PLOTLY_TEMPLATE = "plotly_white"
NORMAL_COLOR = "#2f6f9f"
ANOMALY_COLOR = "#c73535"
THRESHOLD_COLOR = "#8a5a00"


def prepare_telemetry_for_plot(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    plot_df = df.copy()
    plot_df["timestamp"] = pd.to_datetime(plot_df["timestamp"], utc=True)
    plot_df = plot_df.sort_values("timestamp")
    return plot_df


def build_sensor_timeseries(df: pd.DataFrame, metric: str = "motor_current") -> go.Figure:
    plot_df = prepare_telemetry_for_plot(df)
    fig = go.Figure()

    if plot_df.empty or metric not in plot_df.columns:
        fig.update_layout(
            template=PLOTLY_TEMPLATE,
            height=360,
            title="No telemetry available",
        )
        return fig

    normal_df = plot_df[plot_df["anomaly_flag"] != 1]
    anomaly_df = plot_df[plot_df["anomaly_flag"] == 1]

    fig.add_trace(
        go.Scatter(
            x=plot_df["timestamp"],
            y=plot_df[metric],
            mode="lines",
            name=metric.replace("_", " ").title(),
            line={"color": NORMAL_COLOR, "width": 2},
            hovertemplate="%{x}<br>%{y}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=normal_df["timestamp"],
            y=normal_df[metric],
            mode="markers",
            name="Normal readings",
            marker={"color": NORMAL_COLOR, "size": 7, "opacity": 0.75},
            customdata=normal_df[["door_id", "anomaly_flag"]],
            hovertemplate="Door: %{customdata[0]}<br>Value: %{y}<br>Status: Normal<extra></extra>",
        )
    )

    if not anomaly_df.empty:
        fig.add_trace(
            go.Scatter(
                x=anomaly_df["timestamp"],
                y=anomaly_df[metric],
                mode="markers",
                name="Anomaly readings",
                marker={
                    "color": ANOMALY_COLOR,
                    "size": 12,
                    "symbol": "diamond",
                    "line": {"color": "#ffffff", "width": 1},
                },
                customdata=anomaly_df[["door_id", "anomaly_flag"]],
                hovertemplate="Door: %{customdata[0]}<br>Value: %{y}<br>Status: Anomaly<extra></extra>",
            )
        )

    threshold = SENSOR_THRESHOLDS.get(metric)
    if threshold:
        fig.add_hline(
            y=threshold["value"],
            line_dash="dash",
            line_color=THRESHOLD_COLOR,
            annotation_text=f"{threshold['label']}: {threshold['value']}",
            annotation_position="top left",
        )

    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        height=390,
        margin={"l": 10, "r": 10, "t": 48, "b": 20},
        title=f"{metric.replace('_', ' ').title()} Trend",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0},
        xaxis_title=None,
        yaxis_title=metric.replace("_", " ").title(),
    )
    return fig


def build_anomaly_type_bar(summary_report: dict | None) -> go.Figure:
    anomaly_types = (summary_report or {}).get("anomaly_types", {})
    data = pd.DataFrame(anomaly_types.items(), columns=["Fault Type", "Count"])
    if data.empty:
        data = pd.DataFrame([{"Fault Type": "No anomalies", "Count": 0}])

    fig = px.bar(
        data,
        x="Count",
        y="Fault Type",
        orientation="h",
        text="Count",
        color_discrete_sequence=[ANOMALY_COLOR],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=300,
        margin={"l": 10, "r": 10, "t": 20, "b": 20},
        xaxis_title="Anomaly Count",
        yaxis_title=None,
        showlegend=False,
    )
    return fig


def build_door_anomaly_bar(summary_report: dict | None) -> go.Figure:
    affected_doors = (summary_report or {}).get("most_affected_doors", {})
    data = pd.DataFrame(affected_doors.items(), columns=["Door", "Anomalies"])
    if data.empty:
        data = pd.DataFrame([{"Door": "No doors affected", "Anomalies": 0}])

    fig = px.bar(
        data,
        x="Door",
        y="Anomalies",
        text="Anomalies",
        color="Anomalies",
        color_continuous_scale=["#d8e9f5", ANOMALY_COLOR],
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(
        height=300,
        margin={"l": 10, "r": 10, "t": 20, "b": 20},
        xaxis_title=None,
        yaxis_title="Anomaly Count",
        coloraxis_showscale=False,
    )
    return fig


def build_door_metric_heatmap(df: pd.DataFrame, metric: str = "anomaly_flag") -> go.Figure:
    plot_df = prepare_telemetry_for_plot(df)
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(template=PLOTLY_TEMPLATE, height=320, title="No telemetry available")
        return fig

    plot_df["time_bucket"] = plot_df["timestamp"].dt.strftime("%H:%M:%S")
    heatmap_df = (
        plot_df.pivot_table(
            index="door_id",
            columns="time_bucket",
            values=metric,
            aggfunc="sum" if metric == "anomaly_flag" else "mean",
            fill_value=0,
        )
        .sort_index()
    )

    fig = px.imshow(
        heatmap_df,
        aspect="auto",
        color_continuous_scale=["#edf6f9", "#f9c74f", ANOMALY_COLOR],
        template=PLOTLY_TEMPLATE,
        labels={"x": "Time", "y": "Door", "color": "Anomalies"},
    )
    fig.update_layout(
        height=330,
        margin={"l": 10, "r": 10, "t": 30, "b": 20},
        title="Door-Level Anomaly Heatmap",
    )
    return fig


def build_feature_stats_bar(health_report: dict | None) -> go.Figure:
    feature_stats = (health_report or {}).get("feature_stats", {})
    rows = [
        {"Feature": feature, "Mean": stats.get("mean", 0), "Max": stats.get("max", 0)}
        for feature, stats in feature_stats.items()
    ]
    data = pd.DataFrame(rows)
    if data.empty:
        data = pd.DataFrame([{"Feature": "No feature data", "Mean": 0, "Max": 0}])

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=data["Feature"],
            y=data["Mean"],
            name="Mean",
            marker_color=NORMAL_COLOR,
        )
    )
    fig.add_trace(
        go.Bar(
            x=data["Feature"],
            y=data["Max"],
            name="Max",
            marker_color=ANOMALY_COLOR,
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        barmode="group",
        height=330,
        margin={"l": 10, "r": 10, "t": 30, "b": 20},
        title="Feature Statistics",
        xaxis_title=None,
        yaxis_title="Value",
    )
    return fig
