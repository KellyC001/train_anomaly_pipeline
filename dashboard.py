# dashboard.py
import os
import streamlit as st
import pandas as pd
import psycopg2
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

st.set_page_config(page_title="Train System SCADA & Agent Dashboard", layout="wide")
st.title("🚇 LTA Rail Digitalization — Kafka Stream & MCP Controller")

left_panel, right_panel = st.columns([2, 1])

# Initialize Session State tracking variables for our Hook integration
if "last_hook_alert" not in st.session_state:
    st.session_state.last_hook_alert = None

with left_panel:
    st.header("Live SCADA Telemetry Stream")
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            database=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"]
        )
        df = pd.read_sql("SELECT timestamp, door_id, motor_current, vibration, voltage, cycle_duration, anomaly_flag FROM sensor_logs ORDER BY timestamp DESC LIMIT 12", conn)
        conn.close()
        
        def anomaly_styler(row):
            return ['background-color: #ffcccc' if row['anomaly_flag'] == 1 else '' for _ in row]

        st.dataframe(df.style.apply(anomaly_styler, axis=1), use_container_width=True)
        
        if not df.empty:
            st.subheader("Motor Current Load Fluctuations Tracing")
            st.line_chart(df.set_index('timestamp')[['motor_current']])
    except Exception:
        st.info("Waiting for data ingestion... Ensure your Docker containers and consumer script are running.")

with right_panel:
    st.header("🤖 Autonomous Diagnostic Node")
    st.write("Simulating Agent reasoning patterns fueled by your custom PostgreSQL MCP server tools.")
    
    execute_agent = st.button("Run Context-Aware Diagnostics Loop")
    
    if execute_agent:
        with st.spinner("Agent calling MCP Gateway protocols..."):
            try:
                # Agent makes unified calls to the explicit tools exposed by your new MCP microservice
                db_context = requests.get("http://127.0.0.1:8000/tools/query_recent_faults?door_id=Door-A1").json()
                file_context = requests.get("http://127.0.0.1:8000/tools/fetch_engineering_logs?door_id=Door-A1").json()
                
                st.markdown("### 🧩 MCP Resource Extraction Payload:")
                st.json({
                    "target_asset": "Door-A1",
                    "postgres_mart_metrics": db_context[:1] if db_context else "No active database anomalies found.",
                    "filesystem_logs_status": "SUCCESS"
                })
                
                st.markdown("### 📋 Synthesized Agent Diagnostic Conclusion:")
                st.success("""
                **VULNERABILITY LEVEL:** HIGH ALERT REGISTERED  
                
                **ANALYSIS METHODOLOGY:** 1. Isolation Forest output verified. The data point points to a clear physical anomaly (Current draw >7.2 Amps, runtime exceeding nominal limits by 2.1 seconds).  
                2. Cross-referenced structural history logs exposed by the file tools. The entry records an unresolved **+1.5mm physical guide-rail warp**.  
                3. Conclusion: The motor current spike is caused by physical friction along the warped track assembly, not an external obstruction.
                
                **AUTOMATED ACTIONS ROUTED:** - Dispatched urgent component intervention blueprint to maintenance bays.
                - Scheduled alignment calibration checklist for tonight's depot window.
                """)
            except Exception:
                st.error("MCP Server connection timed out. Confirm mcp_server.py is running on port 8000.")