from src.anomaly_model import evaluate_anomaly, train_baseline_model
from src.telemetry import generate_telemetry


def test_normal_telemetry_scores_as_normal():
    model = train_baseline_model()
    telemetry = {
        "motor_current": 2.2,
        "vibration": 0.35,
        "voltage": 24.4,
        "cycle_duration": 3.5,
    }

    anomaly_flag, anomaly_type = evaluate_anomaly(telemetry, model)

    assert anomaly_flag == 0
    assert anomaly_type == "Normal Cycle"


def test_current_spike_is_motor_obstruction_fault():
    model = train_baseline_model()
    telemetry = generate_telemetry("Door-A1")
    telemetry["motor_current"] = 7.5

    anomaly_flag, anomaly_type = evaluate_anomaly(telemetry, model)

    assert anomaly_flag == 1
    assert anomaly_type == "Motor Obstruction Fault"


def test_voltage_sag_is_electrical_supply_fault():
    model = train_baseline_model()
    telemetry = generate_telemetry("Door-A1")
    telemetry["voltage"] = 17.0

    anomaly_flag, anomaly_type = evaluate_anomaly(telemetry, model)

    assert anomaly_flag == 1
    assert anomaly_type == "Electrical Supply Sag"
