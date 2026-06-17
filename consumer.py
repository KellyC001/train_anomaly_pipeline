# consumer.py
import json
import os
import numpy as np
import psycopg2
from kafka import KafkaConsumer
from sklearn.ensemble import IsolationForest

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Setup Postgres database connection (read from environment)
conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["POSTGRES_DB"],
    user=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"]
)
cursor = conn.cursor()

# Create table schema
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sensor_logs (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP,
        door_id VARCHAR(50),
        cycle_state VARCHAR(50),
        motor_current REAL,
        vibration REAL,
        voltage REAL,
        cycle_duration REAL,
        anomaly_flag INTEGER,
        anomaly_type VARCHAR(100)
    );
""")
conn.commit()

# Setup ML Engine (Simulated pre-trained Isolation Forest)
# Normally you'd fit this with standard normal historical data
X_train = np.random.normal(loc=[2.2, 0.35, 24.4, 3.5], scale=[0.2, 0.05, 0.3, 0.2], size=(1000, 4))
clf = IsolationForest(contamination=0.03, random_state=42)
clf.fit(X_train)

# Start listening to Kafka Queue
consumer = KafkaConsumer(
    'train-doors',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

def evaluate_anomaly(metrics):
    # Predict (-1 for anomaly, 1 for normal)
    features = np.array([[metrics['motor_current'], metrics['vibration'], metrics['voltage'], metrics['cycle_duration']]])
    pred = clf.predict(features)[0]
    
    anomaly_flag = 1 if pred == -1 else 0
    anomaly_type = "Normal Cycle"
    
    if anomaly_flag == 1:
        # Categorize the root physical failure
        if metrics['motor_current'] > 4.5:
            anomaly_type = "Motor Obstruction Fault"
        elif metrics['vibration'] > 1.2:
            anomaly_type = "Mechanical Bearing Fault"
        elif metrics['voltage'] < 19.5:
            anomaly_type = "Electrical Supply Sag"
        elif metrics['cycle_duration'] > 5.5:
            anomaly_type = "Cycle Delay / Friction Fault"
        else:
            anomaly_type = "Statistical Multi-Variable Outlier"

    return anomaly_flag, anomaly_type

print("📥 FastAPI Worker listening for new events on topic 'train-doors'...")
for message in consumer:
    raw_telemetry = message.value
    
    # 1. Run Machine Learning Inference
    anomaly_flag, anomaly_type = evaluate_anomaly(raw_telemetry)
    
    # 2. Write straight to database
    cursor.execute("""
        INSERT INTO sensor_logs (timestamp, door_id, cycle_state, motor_current, vibration, voltage, cycle_duration, anomaly_flag, anomaly_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        raw_telemetry['timestamp'],
        raw_telemetry['door_id'],
        raw_telemetry['cycle_state'],
        raw_telemetry['motor_current'],
        raw_telemetry['vibration'],
        raw_telemetry['voltage'],
        raw_telemetry['cycle_duration'],
        anomaly_flag,
        anomaly_type
    ))
    conn.commit()
    
    # 3. THE AUTOMATION HOOK: If an anomaly hits your database, instantly notify the Agent Hub
    if db_flag == 1:
        print(f"⚠️ [Hook Event] Outlier identified on {raw_telemetry['door_id']}. Forwarding payload to Agent application context...")
        try:
            import requests
            requests.post("http://localhost:8501/alert_webhook", json={
                "door_id": str(raw_telemetry['door_id']),
                "motor_current": float(raw_telemetry['motor_current']),
                "vibration": float(raw_telemetry['vibration']),
                "voltage": float(raw_telemetry['voltage']),
                "cycle_duration": float(raw_telemetry['cycle_duration']),
                "anomaly_type": str(anomaly_type)
            })
        except Exception:
            pass

        
    status = f"⚠️ [ANOMALY DETECTED: {anomaly_type}]" if anomaly_flag else "✅ [NORMAL]"
    print(f"[WORKER] Processed {raw_telemetry['door_id']}. Status: {status}")