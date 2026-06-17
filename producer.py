# producer.py
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

DOORS = ["Door-A1", "Door-A2", "Door-B1", "Door-B2"]

def generate_telemetry(door_id, inject_anomaly=None):
    """Generates mock train door telemetry readings."""
    timestamp = datetime.utcnow().isoformat()
    
    # Base normal bounds
    current = round(random.uniform(1.8, 2.6), 2)
    vibration = round(random.uniform(0.2, 0.5), 2)
    voltage = round(random.uniform(23.8, 25.0), 1)
    duration = round(random.uniform(3.2, 3.8), 2)

    # Injected mechanical anomalies
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
        "cycle_duration": duration
    }

if __name__ == "__main__":
    print("🚀 Local Train Door Telemetry Ingestion Simulator Active...")
    try:
        while True:
            # 1. Decide if we randomly introduce an anomaly (5% probability)
            anomaly_trigger = None
            if random.random() < 0.05:
                anomaly_trigger = random.choice(["current", "vibration", "voltage", "duration"])
                print(f"⚠️ [SYSTEM] Simulating anomaly event: {anomaly_trigger}")

            # 2. Pick a random door
            selected_door = random.choice(DOORS)
            payload = generate_telemetry(selected_door, inject_anomaly=anomaly_trigger)
            
            # 3. Stream payload to Kafka Broker
            producer.send('train-doors', value=payload)
            print(f"[PRODUCER] Sent message: {payload}")
            
            # Rate limiting
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("Stopping simulation...")