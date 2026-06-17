# Train Anomaly Pipeline

A lightweight train anomaly detection pipeline using Kafka, PostgreSQL, Streamlit, and FastAPI.

This repository demonstrates real-time data ingestion and anomaly scoring with Kafka, persistent storage in PostgreSQL, and dashboard visualization via Streamlit.

## Features

- Kafka producer and consumer for streaming telemetry data
- Anomaly scoring and persistence in PostgreSQL
- Streamlit dashboard for monitoring anomaly results
- FastAPI microservice for querying and inspecting anomaly data
- Docker Compose support for local Kafka + PostgreSQL infrastructure

## Repository contents

- `producer.py` — produces sample telemetry events to Kafka
- `consumer.py` — consumes Kafka messages, scores anomalies, and stores results in PostgreSQL
- `dashboard.py` — Streamlit UI for querying stored anomaly data
- `mcp_server.py` — FastAPI microservice for DB queries and diagnostics
- `docker-compose.yaml` — local development stack for Kafka, Zookeeper, and PostgreSQL
- `requirements.txt` — Python dependencies
- `.gitignore` — ignores local environment files and artifacts

## Getting started

### Prerequisites

- Python 3.11+ (or a compatible Python 3.x version)
- Docker & Docker Compose
- Git

### Install dependencies

```bash
cd train_anomaly_pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure environment

Create a local `.env` file with your own database and Kafka settings.

Then update any values as needed, especially database credentials.

## Run locally with Docker Compose

Start Kafka, Zookeeper, and PostgreSQL:

```bash
docker compose up -d
```

Confirm the services are running:

```bash
docker compose ps
```

## Run the pipeline components

### Start the producer

```bash
python producer.py
```

### Start the consumer

```bash
python consumer.py
```

### Start the dashboard

```bash
streamlit run dashboard.py
```

### Start the FastAPI service

```bash
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

## Environment variables

The `.env` file should define:

- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_DB`
- `DB_HOST`
- `DB_PORT`
- `KAFKA_ADVERTISED_LISTENERS`

