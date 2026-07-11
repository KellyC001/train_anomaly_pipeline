# RailOps AI Architecture

This project is evolving from a train door anomaly detection demo into a portfolio-ready data and AI engineering system.

## Target System

```text
Train Door Simulator
        |
        v
Kafka Message Stream
        |
        v
Anomaly Detection Worker
        |
        v
PostgreSQL
        |
        +----> Streamlit Operations Dashboard
        |
        +----> FastAPI Diagnostic Tool Gateway
                    |
                    v
              AI Diagnostic Agent
                    |
                    +----> Maintenance Knowledge Base
                    +----> Structured Incident Report
                    +----> Human Review Workflow
```

## Portfolio Skill Map

| Area | What this project will show | Why it is useful |
| --- | --- | --- |
| Data science | Anomaly detection, feature metrics, model comparison | Shows that model output is evaluated and explainable |
| Data engineering | Streaming ingestion, PostgreSQL storage, workflow orchestration | Shows reliable movement of data through a system |
| MLOps | Model metadata, data drift checks, monitoring reports | Shows awareness that models need production monitoring |
| AI engineering | Tool-calling agent, RAG, structured JSON diagnoses | Shows modern LLM application design beyond chat prompts |
| Product thinking | Dashboard, incident workflow, human review loop | Shows how technical output becomes useful to operators |

## Build Phases

1. Foundation cleanup: reusable modules, tests, config, database helpers.
2. Orchestration: add scheduled Prefect flows for ingestion checks, model metrics, and reports.
3. Monitoring: add drift and quality reports for telemetry and anomaly outputs.
4. Agent tools: expose database and maintenance context as callable tools.
5. RAG diagnosis: retrieve fault manuals and maintenance notes before generating recommendations.
6. Incident workflow: create structured incident reports with human approval and feedback.

## Current Foundation

The core pipeline now has reusable modules:

- `src/telemetry.py`: synthetic train door telemetry generator
- `src/anomaly_model.py`: baseline Isolation Forest model and anomaly classification
- `src/database.py`: PostgreSQL schema, inserts, and query helpers
- `src/config.py`: environment-backed settings

The legacy runnable entrypoints remain:

- `producer.py`
- `consumer.py`
- `dashboard.py`
- `mcp_server.py`

## Prefect Orchestration

`orchestration.py` adds three report-oriented Prefect flows:

| Flow | Purpose | Default schedule |
| --- | --- | --- |
| `daily-anomaly-summary` | Summarizes anomaly count, anomaly rate, affected doors, and latest anomalies | Daily at 08:00 |
| `data-quality-check` | Checks missing values, duplicate readings, invalid ranges, and schema expectations | Hourly |
| `model-health-report` | Tracks anomaly rate and feature distributions for model monitoring | Daily at 08:30 |

There is also a combined `railops-daily-operations` flow that generates all three reports in one run.

These flows write JSON reports into `reports/` so the project has inspectable artifacts for demos, screenshots, and dashboard integration.

See `docs/PREFECT_ORCHESTRATION.md` for run commands and schedules.

## Presentation Layer

The dashboard is organized by decision need:

| Tab | Audience | Question answered |
| --- | --- | --- |
| Command Center | Manager / operations lead | Is anything wrong right now, and where should we look first? |
| Monitoring Health | Data analyst / data owner | Can we trust the dashboard and the underlying data? |
| Telemetry Explorer | Analyst / engineer | What do the detailed sensor readings show? |
| AI Diagnostics | AI engineering demo | What tool outputs can a future LLM agent use for explanations? |

Streamlit provides the dashboard shell, while Plotly provides the interactive visualization layer for threshold-aware sensor trends, anomaly markers, affected-door charts, and model-health charts.
