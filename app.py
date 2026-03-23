import streamlit as st
import yfinance as yf
import pandas as pd
import asyncio
import psycopg2
from research_graph import graph
from expert_registry import ExpertiseRegistry
import os
import json
# --- INITIALIZATION ---
st.set_page_config(page_title="GenAI Equity Research Command Center", layout="wide", page_icon="🏦")
registry = ExpertiseRegistry()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_UPLOADS_DIR = os.path.join(BASE_DIR, "raw_uploads")
CHUB_DOCS_DIR = os.path.join(BASE_DIR, "chub_content", "documents")

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stAlert { margin-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 GenAI Equity Research Command Center")
st.caption("Powered by LangGraph, Context Hub, and Postgres AIOps")

# --- DATA FETCHING ---
def fetch_price_history(ticker_symbol):
    df = yf.download(ticker_symbol, period="1mo", interval="1d")
    if df.empty: return pd.DataFrame()
    df.columns = df.columns.get_level_values(0) 
    df = df.reset_index()
    return df[['Date', 'Close']]

# Create Tabs for the UI
tab1, tab2 = st.tabs(["📊 Manual Research", "🚨 Live Auditor Swarm"])

# ==========================================
# TAB 1: MANUAL RESEARCH (With A2UI)
# ==========================================
with tab1:
    with st.sidebar:
        st.header("Research Parameters")
        ticker = st.text_input("Enter Ticker (e.g. HDFCBANK.NS)", value="HDFCBANK.NS")
        
        st.markdown("### 🎭 Select Agent Lens")
        st.caption("Override the default routing to change how the agent thinks.")
        
        persona_options = ["Auto-Route"] + list(registry.registry_map.keys())
        selected_label = st.selectbox("Expertise Source", options=persona_options)
        
        if selected_label == "Auto-Route":
            persona_id = registry.get_skill_id(ticker)
        else:
            persona_id = registry.registry_map[selected_label]
            
        expert_context = registry.fetch_resource(persona_id)
        
        st.markdown("---")
        st.markdown("### 🧠 Active Knowledge Base")
        with st.expander(f"View Active Persona: {selected_label}", expanded=False):
            st.markdown(expert_context)
            st.caption(f"Source Path: {persona_id}")

        run_button = st.button("Generate Research Report", type="primary")
        
        st.markdown("---")
        st.markdown("### 📡 System Status")
        st.status("PostgreSQL: Connected", state="complete")
        st.status("Context Hub (Chub): Active", state="complete")
        st.markdown("---")
        st.markdown("### 📁 Knowledge Vault Ingestion")
        uploaded_file = st.file_uploader("Upload New Research PDF", type="pdf")

        if uploaded_file:
            if st.button(f"Index for {ticker}"):
                with st.spinner(f"Reading and Mapping {ticker} documents..."):
                    # Ensure directories exist relatively
                    if not os.path.exists(RAW_UPLOADS_DIR):
                        os.makedirs(RAW_UPLOADS_DIR)
            
                    # Use relative save path
                    save_path = os.path.join(RAW_UPLOADS_DIR, uploaded_file.name)
            
                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
    
                    # 2. Trigger ingestion
                    from process_document import ingest_pdf_to_chub
                    page_map = ingest_pdf_to_chub(save_path, ticker)
    
                    # 3. Update Master Index JSON relatively
                    index_path = os.path.join(CHUB_DOCS_DIR, "master_index.json")
                    existing_index = {}
                    if os.path.exists(index_path):
                        with open(index_path, "r") as f:
                            existing_index = json.load(f)
    
                    existing_index[ticker] = page_map
                    with open(index_path, "w") as f:
                        json.dump(existing_index, f, indent=4)
        
                    st.success(f"✅ {ticker} knowledge updated!")

    if run_button:
        with st.expander("🕵️ View Agent Collaboration Log", expanded=True):
            log_container = st.empty()

        async def run_full_research():
            status_text = "" 
            full_state = {}
            initial_state = {
                "ticker": ticker, 
                "raw_data": "", 
                "sentiment_data": "", 
                "analysis": "",
                "persona_id": persona_id 
            }

            async for event in graph.astream(initial_state, stream_mode="values"):
                full_state = event 
                if event.get("raw_data") and "Data Gatherer:" not in status_text:
                    status_text += "✅ **Data Gatherer:** Retrieved PostgreSQL records via MCP.\n"
                if event.get("sentiment_data") and "Sentiment Analyzer:" not in status_text:
                    status_text += "✅ **Sentiment Analyzer:** Analyzed Market News.\n"
                if event.get("analysis") and "Financial Analyst:" not in status_text:
                    status_text += f"✅ **Financial Analyst:** Generating UI Payload and Thesis...\n"
                
                log_container.markdown(status_text)
            return full_state

        with st.spinner(f"Initiating Elite Swarm for {ticker}..."):
            result = asyncio.run(run_full_research())
            history = fetch_price_history(ticker)

        st.subheader(f"📈 30-Day Price Trend: {ticker}")
        if not history.empty:
            m1, m2 = st.columns(2)
            current_p = float(history['Close'].iloc[-1])
            prev_p = float(history['Close'].iloc[-2])
            m1.metric(label="Current Price", value=f"₹{current_p:.2f}", delta=f"{(current_p - prev_p):.2f}")
            st.line_chart(history, x="Date", y="Close")

        st.markdown("---")

        col_metrics, col_sentiment = st.columns(2)
        with col_metrics:
            st.subheader("📑 Internal Records")
            st.code(result.get('raw_data', ''), language="text")
                
        with col_sentiment:
            st.subheader("🎭 Market Sentiment")
            st.markdown(result.get('sentiment_data', ''))

        st.markdown("---")
        
        # 🔥 THE GENERATIVE UI RENDERER 🔥
        ui = result.get('ui_payload', {})
        rec = ui.get('recommendation', 'HOLD')
        status = ui.get('status', 'success')
        metrics = ui.get('key_metrics', [])

        # 1. Dynamic Alert Banner
        if status == "error":
            st.error("🚨 **AGENT ALERT: Critical Weakness or Crash Detected.**")
        elif status == "warning":
            st.warning("⚠️ **AGENT NOTICE: Elevated Volatility Predicted.**")
        else:
            st.success("✅ **AGENT VERDICT: Fundamentals Remain Stable.**")

        # 2. Dynamic Metric Highlights
        if metrics:
            st.markdown("### 🎯 Key Focus Areas")
            cols = st.columns(len(metrics))
            for idx, m in enumerate(metrics):
                cols[idx].metric(label=m.get('label', 'Metric'), value=m.get('value', 'N/A'))
            st.markdown("---")

        st.subheader("🤖 Agentic Investment Thesis")
        analysis_col, expert_col = st.columns([2, 1])
        
        with analysis_col:
            color = "green" if rec == "BUY" else "red" if rec == "SELL" else "orange"
            st.markdown(f"#### Recommendation: <span style='color:{color}'>{rec}</span>", unsafe_allow_html=True)
            st.write(result.get('analysis', ''))
        
        with expert_col:
            final_persona_used = result.get('active_persona', persona_id)
            st.info(f"💡 **Lens Applied: {final_persona_used}**")
            st.caption("The Analyst Agent followed these specific guidelines retrieved from the Context Hub:")
            st.markdown(f"> {expert_context[:300]}...")
            st.button("Verified by Hub", disabled=True, key="manual_hub_button")
        st.markdown("---")
        
        # 🔥 THE PDF EXPORTER 🔥
        try:
            from report_generator import generate_pdf_report
            from datetime import datetime
            
            pdf_bytes = generate_pdf_report(result, ticker)
            
            st.download_button(
                label="📥 Download Executive Briefing (PDF)",
                data=pdf_bytes,
                file_name=f"HDFC_Research_{ticker}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Failed to generate PDF: {e}")

    else:
        st.info("👈 Select a persona from the sidebar, enter a ticker, and click Generate.")


# ==========================================
# TAB 2: LIVE AUDITOR SWARM (With A2UI)
# ==========================================
with tab2:
    st.markdown("### 📡 Autonomous Database Monitor")
    st.write("This tab simulates the background Auditor. It watches the PostgreSQL database for sudden price drops.")
    
    def fetch_live_db():
        conn = psycopg2.connect(dbname="airflow", user="airflow", password="airflow", host="127.0.0.1", port="5435")
        query = """
            SELECT DISTINCT ON (ticker) ticker, current_price, pe_ratio 
            FROM equity_metrics 
            ORDER BY ticker, ingestion_timestamp DESC;
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    if "baseline_prices" not in st.session_state:
        st.session_state.baseline_prices = {}

    col_btn, col_info = st.columns([1, 4])
    refresh_btn = col_btn.button("🔄 Poll Database Now")
    
    if refresh_btn:
        live_data = fetch_live_db()
        cols = st.columns(len(live_data))
        crash_detected = None
        
        for idx, row in live_data.iterrows():
            t = row['ticker']
            p = row['current_price']
            
            if t not in st.session_state.baseline_prices:
                st.session_state.baseline_prices[t] = p
                
            baseline = st.session_state.baseline_prices[t]
            pct_change = ((p - baseline) / baseline) * 100 if baseline else 0
            
            cols[idx].metric(label=t, value=f"₹{p:.2f}", delta=f"{pct_change:.2f}%")
            
            if pct_change < -2.0:
                crash_detected = t
                
        if crash_detected:
            st.error(f"⚠️ CRITICAL ALERT: Market anomaly detected for {crash_detected}. Waking up Agent Swarm...")
            
            with st.spinner(f"Agent generating full forensic report for {crash_detected}..."):
                initial_state = {"ticker": crash_detected, "raw_data": "", "sentiment_data": "", "analysis": ""}
                result = asyncio.run(graph.ainvoke(initial_state))
                
                history = fetch_price_history(crash_detected)
                crash_persona_id = registry.get_skill_id(crash_detected)
                expert_context = registry.fetch_resource(crash_persona_id)
                
                st.markdown(f"## 🚨 Emergency Forensic Report: {crash_detected}")
                
                if not history.empty:
                    st.markdown("### 📈 30-Day Price Trend")
                    st.line_chart(history, x="Date", y="Close")

                st.markdown("---")

                col_metrics, col_sentiment = st.columns(2)
                with col_metrics:
                    st.subheader("📑 Internal Records")
                    st.code(result.get('raw_data', ''), language="text")
                        
                with col_sentiment:
                    st.subheader("🎭 Market Sentiment")
                    st.markdown(result.get('sentiment_data', ''))

                st.markdown("---")
                
                # 🔥 THE GENERATIVE UI RENDERER FOR TAB 2 🔥
                ui = result.get('ui_payload', {})
                rec = ui.get('recommendation', 'HOLD')
                status = ui.get('status', 'error') # Default to error in tab 2 since it's a crash monitor
                metrics = ui.get('key_metrics', [])

                if metrics:
                    st.markdown("### 🎯 Key Focus Areas")
                    m_cols = st.columns(len(metrics))
                    for idx, m in enumerate(metrics):
                        m_cols[idx].metric(label=m.get('label', 'Metric'), value=m.get('value', 'N/A'))
                    st.markdown("---")

                st.subheader("🤖 Agentic Investment Thesis")
                analysis_col, expert_col = st.columns([2, 1])
                
                with analysis_col:
                    color = "green" if rec == "BUY" else "red" if rec == "SELL" else "orange"
                    st.markdown(f"#### Action Required: <span style='color:{color}'>{rec}</span>", unsafe_allow_html=True)
                    st.write(result.get('analysis', '')) 
                
                with expert_col:
                    st.info(f"💡 **Identity Loaded: {crash_persona_id}**")
                    st.caption("The Agent applied these specific guidelines from the Context Hub to analyze the crash:")
                    st.markdown(f"> {expert_context[:300]}...")
                    st.button("Verified by Hub", disabled=True, key="live_hub_button")
                st.markdown("---")
                
                # 🔥 EMERGENCY PDF EXPORTER FOR TAB 2 🔥
                try:
                    from report_generator import generate_pdf_report
                    from datetime import datetime
                    
                    # Generate the PDF specifically for the crashed ticker
                    pdf_bytes_emergency = generate_pdf_report(result, crash_detected)
                    
                    st.download_button(
                        label=f"📥 Download Emergency Forensic Report ({crash_detected})",
                        data=pdf_bytes_emergency,
                        file_name=f"CRASH_REPORT_{crash_detected}_{datetime.now().strftime('%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        key="emergency_pdf_button" # Unique key to avoid conflict with Tab 1
                    )
                except Exception as e:
                    st.error(f"Failed to generate Emergency PDF: {e}")
                
            st.session_state.baseline_prices[crash_detected] = float(live_data.loc[live_data['ticker'] == crash_detected, 'current_price'].iloc[0])
        else:
            st.success("✅ All monitored equities are stable.")