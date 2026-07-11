from src.telemetry import generate_telemetry


def test_generated_telemetry_has_expected_fields():
    telemetry = generate_telemetry("Door-A1")

    assert set(telemetry) == {
        "timestamp",
        "door_id",
        "cycle_state",
        "motor_current",
        "vibration",
        "voltage",
        "cycle_duration",
    }
    assert telemetry["door_id"] == "Door-A1"
    assert telemetry["cycle_state"] == "CLOSING"


def test_current_anomaly_pushes_current_outside_normal_range():
    telemetry = generate_telemetry("Door-A1", inject_anomaly="current")

    assert telemetry["motor_current"] >= 6.0
