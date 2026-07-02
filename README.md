# Train Anomaly Pipeline

A demonstration project that shows how train door sensor data can be monitored in real time to detect unusual behaviour.

The system simulates train door telemetry, checks each reading for possible anomalies, stores the results, and displays them in a dashboard for monitoring and diagnosis.

## What This Project Does

This project models a simple railway monitoring workflow:

1. Simulated train door sensor readings are generated.
2. The readings are streamed into a real-time messaging system.
3. Each reading is checked for abnormal behaviour.
4. Results are saved into a database.
5. A dashboard shows recent readings and highlights potential issues.
6. A small diagnostic service provides supporting context for investigation.

The goal is to demonstrate how real-time data pipelines can support condition monitoring, early fault detection, and maintenance decision-making.

## Example Use Case

Imagine a train door begins taking longer than usual to close, or its motor current rises above normal levels.

This pipeline can flag that reading as suspicious and classify it as a possible mechanical, electrical, or operational fault. Maintenance teams could then use the dashboard and diagnostic tools to investigate the issue before it becomes more serious.

## Project Components

| Component | Purpose |
| --- | --- |
| `producer.py` | Simulates train door sensor readings |
| `consumer.py` | Reads the sensor data, checks for anomalies, and saves results |
| `dashboard.py` | Displays recent telemetry and anomaly results |
| `mcp_server.py` | Provides simple diagnostic API endpoints |
| `docker-compose.yaml` | Starts the local Kafka and PostgreSQL services |
| `requirements.txt` | Lists the Python packages needed |

## How The System Works

```text
Simulated Train Data
        |
        v
Kafka Message Stream
        |
        v
Anomaly Detection Worker
        |
        v
PostgreSQL Database
        |
        +----> Streamlit Dashboard
        |
        +----> Diagnostic API Service
```

## Technologies Used

- Python
- Apache Kafka
- PostgreSQL
- Streamlit
- FastAPI
- Scikit-learn
- Docker Compose

## Running The Project Locally

### 1. Install Python Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project folder with the required database settings:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=traindb
DB_HOST=localhost
DB_PORT=5432
```

### 3. Start Supporting Services

```bash
docker compose up -d
```

This starts Kafka, Zookeeper, and PostgreSQL.

### 4. Start The Data Producer

```bash
python producer.py
```

This begins generating simulated train door sensor readings.

### 5. Start The Anomaly Consumer

```bash
python consumer.py
```

This reads the incoming data, checks for anomalies, and stores the results.

### 6. Start The Dashboard

```bash
streamlit run dashboard.py
```

### 7. Start The Diagnostic API

```bash
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

## Notes

This is a demonstration project. The data is simulated, and the anomaly detection model is trained on generated sample data rather than real historical train telemetry.

For a production system, this would need real sensor data, stronger validation, monitoring, security controls, and a properly trained model.

## License

Add your chosen license here.
