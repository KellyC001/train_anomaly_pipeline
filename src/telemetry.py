import random
from datetime import datetime, timezone

DOORS = ["Door-A1", "Door-A2", "Door-B1", "Door-B2"]
ANOMALY_TYPES = ["current", "vibration", "voltage", "duration"]


def generate_telemetry(door_id: str, inject_anomaly: str | None = None) -> dict:
    """Generate one synthetic train door telemetry reading."""
    timestamp = datetime.now(timezone.utc).isoformat()

    current = round(random.uniform(1.8, 2.6), 2)
    vibration = round(random.uniform(0.2, 0.5), 2)
    voltage = round(random.uniform(23.8, 25.0), 1)
    duration = round(random.uniform(3.2, 3.8), 2)

    if inject_anomaly == "current":
        current = round(random.uniform(6.0, 8.0), 2)
    elif inject_anomaly == "vibration":
        vibration = round(random.uniform(1.5, 2.5), 2)
    elif inject_anomaly == "voltage":
        voltage = round(random.uniform(16.0, 18.5), 1)
    elif inject_anomaly == "duration":
        duration = round(random.uniform(6.5, 8.0), 2)

    return {
        "timestamp": timestamp,
        "door_id": door_id,
        "cycle_state": "CLOSING",
        "motor_current": current,
        "vibration": vibration,
        "voltage": voltage,
        "cycle_duration": duration,
    }


def choose_random_anomaly(probability: float = 0.05) -> str | None:
    """Return a random anomaly type at the requested probability."""
    if random.random() < probability:
        return random.choice(ANOMALY_TYPES)
    return None
