import json
import random
import time

from kafka import KafkaProducer

from src.config import settings
from src.telemetry import DOORS, choose_random_anomaly, generate_telemetry


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=[settings.kafka_bootstrap_servers],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def run() -> None:
    producer = build_producer()
    print("Local train door telemetry simulator active.")

    try:
        while True:
            anomaly_trigger = choose_random_anomaly(probability=0.05)
            if anomaly_trigger:
                print(f"[SYSTEM] Simulating anomaly event: {anomaly_trigger}")

            selected_door = random.choice(DOORS)
            payload = generate_telemetry(selected_door, inject_anomaly=anomaly_trigger)

            producer.send(settings.kafka_topic, value=payload)
            print(f"[PRODUCER] Sent message: {payload}")

            time.sleep(2.0)
    except KeyboardInterrupt:
        print("Stopping simulation...")
    finally:
        producer.close()


if __name__ == "__main__":
    run()
