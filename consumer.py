import json

import requests
from kafka import KafkaConsumer

from src.anomaly_model import evaluate_anomaly, train_baseline_model
from src.config import settings
from src.database import ensure_schema, get_db_connection, insert_sensor_log


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        settings.kafka_topic,
        bootstrap_servers=[settings.kafka_bootstrap_servers],
        auto_offset_reset="latest",
        value_deserializer=lambda message: json.loads(message.decode("utf-8")),
    )


def notify_dashboard(telemetry: dict, anomaly_type: str) -> None:
    try:
        requests.post(
            settings.dashboard_alert_webhook,
            json={
                "door_id": str(telemetry["door_id"]),
                "motor_current": float(telemetry["motor_current"]),
                "vibration": float(telemetry["vibration"]),
                "voltage": float(telemetry["voltage"]),
                "cycle_duration": float(telemetry["cycle_duration"]),
                "anomaly_type": str(anomaly_type),
            },
            timeout=3,
        )
    except requests.RequestException:
        pass


def run() -> None:
    conn = get_db_connection()
    ensure_schema(conn)
    model = train_baseline_model()
    consumer = build_consumer()

    print(f"Worker listening for events on Kafka topic '{settings.kafka_topic}'...")
    try:
        for message in consumer:
            telemetry = message.value
            anomaly_flag, anomaly_type = evaluate_anomaly(telemetry, model)
            insert_sensor_log(conn, telemetry, anomaly_flag, anomaly_type)

            if anomaly_flag == 1:
                print(
                    f"[Hook Event] Outlier identified on {telemetry['door_id']}. "
                    "Forwarding payload to agent context..."
                )
                notify_dashboard(telemetry, anomaly_type)

            status = f"[ANOMALY DETECTED: {anomaly_type}]" if anomaly_flag else "[NORMAL]"
            print(f"[WORKER] Processed {telemetry['door_id']}. Status: {status}")
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    run()
