# Prefect Orchestration

This project uses Prefect to turn operational checks into scheduled, observable workflows.

The goal is not just to run scripts. The goal is to show how a data and AI system can be monitored, summarized, and prepared for downstream agent workflows.

## Flows

| Flow | Command | What it produces | Skill showcased |
| --- | --- | --- | --- |
| `daily-anomaly-summary` | `python orchestration.py daily` | Anomaly counts, anomaly rate, affected doors, latest anomalies | Data product reporting |
| `data-quality-check` | `python orchestration.py quality` | Missing values, duplicates, invalid ranges, schema checks | Data engineering reliability |
| `model-health-report` | `python orchestration.py health` | Feature statistics, anomaly rate, rule thresholds | MLOps monitoring |
| `railops-daily-operations` | `python orchestration.py all` | All reports in one run | Workflow orchestration |

Reports are written to `reports/` as JSON files.

The Streamlit dashboard reads the latest JSON report for each report type and displays the results in:

- **Command Center** for manager-facing anomaly status
- **Monitoring Health** for data quality and model monitoring checks

Plotly charts make the report outputs easier to inspect: anomaly markers are highlighted, threshold lines are visible, and affected doors/fault types are summarized visually.

## Run Once

Start the local infrastructure first:

```bash
docker compose up -d
```

Generate telemetry and consume it into PostgreSQL:

```bash
python producer.py
python consumer.py
```

Then run the operations flow:

```bash
python orchestration.py all
```

## Run On A Schedule

Start scheduled deployments:

```bash
python orchestration.py serve
```

Default schedules:

- Data quality check: hourly
- Daily anomaly summary: every day at 08:00
- Model health report: every day at 08:30

## Why This Matters

This layer demonstrates that the anomaly detection system can be operated like a real data product:

- It has repeatable scheduled checks.
- It creates durable report artifacts.
- It separates data quality, model health, and anomaly reporting.
- It prepares structured outputs that can later feed an AI diagnostic agent.
- It makes those operational checks visible in the dashboard for non-engineering stakeholders.
