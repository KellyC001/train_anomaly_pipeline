import numpy as np
from sklearn.ensemble import IsolationForest

FEATURE_COLUMNS = ["motor_current", "vibration", "voltage", "cycle_duration"]


def train_baseline_model(random_state: int = 42) -> IsolationForest:
    """Train a small synthetic baseline model for demo anomaly scoring."""
    rng = np.random.default_rng(random_state)
    training_data = rng.normal(
        loc=[2.2, 0.35, 24.4, 3.5],
        scale=[0.2, 0.05, 0.3, 0.2],
        size=(1000, len(FEATURE_COLUMNS)),
    )
    model = IsolationForest(contamination=0.03, random_state=random_state)
    model.fit(training_data)
    return model


def build_feature_array(metrics: dict) -> np.ndarray:
    return np.array([[metrics[column] for column in FEATURE_COLUMNS]])


def classify_anomaly_type(metrics: dict, anomaly_flag: int) -> str:
    if anomaly_flag != 1:
        return "Normal Cycle"

    if metrics["motor_current"] > 4.5:
        return "Motor Obstruction Fault"
    if metrics["vibration"] > 1.2:
        return "Mechanical Bearing Fault"
    if metrics["voltage"] < 19.5:
        return "Electrical Supply Sag"
    if metrics["cycle_duration"] > 5.5:
        return "Cycle Delay / Friction Fault"
    return "Statistical Multi-Variable Outlier"


def has_rule_based_fault(metrics: dict) -> bool:
    return (
        metrics["motor_current"] > 4.5
        or metrics["vibration"] > 1.2
        or metrics["voltage"] < 19.5
        or metrics["cycle_duration"] > 5.5
    )


def evaluate_anomaly(metrics: dict, model: IsolationForest | None = None) -> tuple[int, str]:
    """Score one telemetry reading and return anomaly flag plus diagnosis label."""
    model = model or train_baseline_model()
    prediction = model.predict(build_feature_array(metrics))[0]
    anomaly_flag = 1 if prediction == -1 or has_rule_based_fault(metrics) else 0
    return anomaly_flag, classify_anomaly_type(metrics, anomaly_flag)
