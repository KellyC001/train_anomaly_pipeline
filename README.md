# RailOps AI 🚆

<img width="2816" height="1536" alt="train_anomaly_image" src="https://github.com/user-attachments/assets/74940d4c-0478-45c8-abb8-8d1b7c6d6bb0" />

I’ve always been a bit of a nerd about how physical things work. Motors, switches and moving parts are the kind of things that make me stop and wonder, “What would cause this to break?”

With more everyday machines being fitted with sensors, one question stuck with me: **when a simple motor starts struggling, does it suddenly stop working—or does it leave small clues first?**

Maybe it begins drawing more electricity. Maybe it vibrates more than usual or takes slightly longer to complete the same movement. These changes might not look serious on their own, but could they tell us that something is beginning to go wrong?

I chose a train door as my example. It is basically a door powered by a motor, opening and closing again and again throughout the day. It sounds simple, but when one stops working, it can delay a journey and become a much bigger operational problem.

I started by creating pretend sensor readings for things like motor current, vibration, voltage and how long the door takes to close. Once I had the readings, the data-science part naturally followed: could I use them to tell the difference between normal behaviour and something worth checking?

That small question slowly became a much larger investigation. I ended up building a system that generates live readings, looks for unusual behaviour, keeps a history of what happened and shows the results on a dashboard.

> **A quick note about the data:** Everything in this project is simulated. It does not use information from a real train, railway operator or maintenance system.

## What I was curious to find out

- What clues might a motor give us before it stops working?
- Can sensors help us notice those clues earlier?
- How do we move readings from a machine into something people can understand?
- How can we avoid raising an alarm every time a reading looks slightly unusual?
- What information would actually help someone decide what to inspect?

## What I ended up building

To explore those questions, I built:

- A simulator that creates pretend readings from several train doors
- A live stream that moves those readings through the system
- An anomaly check that flags readings that look unusual
- A database that keeps a history of what happened
- Health checks to make sure the data and monitoring system are still working
- A dashboard showing which doors may need attention and why
- A small diagnostic service that a future AI assistant could use to explain what happened

## A simple example

Imagine that a train door begins taking longer than usual to close, or its motor starts drawing more current than normal.

One odd reading does not automatically mean that the door is broken. The system records the reading, checks whether it looks unusual and shows the surrounding information on the dashboard. Someone investigating the issue can then look at the door’s recent history, see which signal changed and decide whether it is worth inspecting.

That is the main idea behind RailOps AI: use small sensor clues to make an emerging problem easier to notice and understand.

## Architecture

![RailOps AI architecture](docs/assets/railops_ai_architecture.svg)

Once my small motor question grew into a complete system, this is how the pieces fitted together:

- **Producer** creates pretend train-door sensor readings.
- **Kafka** acts like a live conveyor belt carrying each new reading.
- **Zookeeper** helps coordinate Kafka in this local setup.
- **Consumer** picks up the readings, checks them for anomalies and saves the results.
- **PostgreSQL** keeps the processed readings and becomes the system’s source of truth.
- **Prefect** runs scheduled checks and creates snapshots for anomalies, data quality and model health.
- **Streamlit + Plotly** turn the stored results into an interactive operations dashboard.
- **FastAPI** provides diagnostic tools for recent faults and maintenance context.
- A **future AI assistant** could use those tools to produce a plain-English incident summary. This part is not fully implemented yet.

## Project components

For anyone who wants to look under the hood, these are the main parts of the repository:

| Component | Purpose |
| --- | --- |
| `producer.py` | Simulates train-door sensor readings |
| `consumer.py` | Reads the sensor data, checks for anomalies and saves the results |
| `dashboard.py` | Shows anomaly status, monitoring health, telemetry and diagnostic context |
| `mcp_server.py` | Provides simple diagnostic API endpoints |
| `src/` | Contains reusable telemetry, anomaly model, database, reporting and visualization modules |
| `tests/` | Tests telemetry, anomaly scoring, reporting, report loading and Plotly charts |
| `docs/ARCHITECTURE.md` | Explains the target architecture and build phases |
| `docs/assets/railops_ai_architecture.svg` | Contains the architecture diagram used above |
| `orchestration.py` | Runs Prefect flows for anomaly summaries, model health and data quality checks |
| `docker-compose.yaml` | Starts the local Kafka and PostgreSQL services |
| `requirements.txt` | Lists the Python packages needed to run the project |

## How the system works now

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
        +----> Prefect Reports
        |
        +----> Streamlit + Plotly Dashboard
        |
        +----> Diagnostic API Service
```

In simple terms, a pretend sensor reading is created, moved through the live stream, checked and stored. The saved readings can then be used by the scheduled reports, dashboard and diagnostic service without each part needing to talk directly to the simulated train door.

## Tools I used

- Python
- Apache Kafka
- PostgreSQL
- Streamlit
- Plotly
- FastAPI
- Scikit-learn
- Prefect
- Docker Compose

## Dashboard views

I organised the dashboard around the questions someone might ask while investigating an issue:

| View | Main question | Intended user |
| --- | --- | --- |
| Command Center | Is anything unusual happening right now, and where should I look first? | Manager / operations lead |
| Monitoring Health | Can I trust the dashboard and the data behind it? | Data analyst / data owner |
| Telemetry Explorer | What do the individual sensor readings show? | Analyst / engineer |
| AI Diagnostics | What evidence could a future AI assistant use to explain the issue? | AI engineering exploration |

The dashboard uses Plotly to show:

- Red anomaly markers
- Sensor trends with warning thresholds
- Doors affected by recent anomalies
- Different anomaly types
- Door-level anomaly heatmaps
- Model-health feature charts

## What I want to explore next

This investigation has given me several directions I would like to take further:

- **Data science:** Try different ways of detecting anomalies and judging whether the results are actually useful.
- **Data engineering:** Make the live stream, database and scheduled checks more reliable when something fails.
- **AI engineering:** Let an AI assistant call the diagnostic tools and turn the evidence into a structured summary, with a person still making the final decision.
- **Product thinking:** Improve the dashboard and incident flow so that an anomaly leads naturally to the next useful action.

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the target architecture and build phases.
See [`docs/PREFECT_ORCHESTRATION.md`](docs/PREFECT_ORCHESTRATION.md) for the orchestration runbook.

## Running the project locally

### 1. Install the Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure the environment variables

Create a `.env` file in the project folder with the required database settings:

```env
POSTGRES_USER=user
POSTGRES_PASSWORD=replace_with_your_local_password
POSTGRES_DB=traindb
DB_HOST=localhost
DB_PORT=5432
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=train-doors
DASHBOARD_ALERT_WEBHOOK=http://localhost:8501/alert_webhook
REPORTS_DIR=reports
```

### 3. Start the supporting services

```bash
docker compose up -d
```

This starts Kafka, Zookeeper and PostgreSQL.

### 4. Start the consumer

```bash
python consumer.py
```

The consumer listens to Kafka, checks the telemetry and writes the results to PostgreSQL.

### 5. Start the data producer

```bash
python producer.py
```

The producer begins generating simulated train-door sensor readings.

### 6. Start the dashboard

```bash
streamlit run dashboard.py
```

### 7. Start the diagnostic API

```bash
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

### 8. Run the Prefect operations flows

Generate all local operations reports:

```bash
python orchestration.py all
```

Run individual flows:

```bash
python orchestration.py daily
python orchestration.py quality
python orchestration.py health
```

Start scheduled local deployments:

```bash
python orchestration.py serve
```

Reports are written as JSON files in the `reports/` folder by default.

After generating the reports, refresh the Streamlit dashboard:

- **Command Center** shows whether action is needed, how many anomalies were found and which doors or faults to inspect first.
- **Monitoring Health** shows whether the dashboard data is complete, recent and trustworthy.
- **Telemetry Explorer** shows the detailed sensor readings.
- **AI Diagnostics** shows the API outputs that a future AI assistant could summarize.

## Honest limitations

- All of the data is generated, so the project cannot prove what a real train-door failure would look like.
- The anomaly-detection model is trained on simulated examples rather than real maintenance history.
- A real system would need properly calibrated sensors, stronger testing, security controls and much more careful validation.
- The AI assistant is not fully implemented. FastAPI currently provides the diagnostic tools that it could call in the future.
- This project explores how the pieces could work together; it is not a production railway-monitoring system.

## Run the tests

```bash
pytest
```

## License

A license has not been selected yet.
