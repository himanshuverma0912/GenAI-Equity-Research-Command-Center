# 🏦 GenAI Equity Research Command Center

An enterprise-grade, agentic workstation designed to automate deep-dive equity research. This system synthesizes structured SQL data, unstructured financial transcripts, and live market sentiment into actionable, branded executive briefings. 

## 🚀 Key Architectural Pillars

### 1. **The Swarm (Multi-Agent Orchestration)**
Powered by **LangGraph**, the system utilizes a specialized swarm of agents to ensure separation of concerns and high-fidelity reasoning:
* **Data Gatherer:** Securely fetches internal metrics (P/E, Market Cap) from a PostgreSQL database via **MCP (Model Context Protocol)**. 
* **Document Researcher:** Employs a **Vectorless PageIndex** to reason over which specific pages of an earnings call or annual report to read, avoiding the noise of traditional Vector RAG. 
* **Sentiment Analyzer:** Scrapes live news to quantify market mood using NLP. 
* **Financial Analyst:** The core engine that synthesizes all inputs into a structured JSON payload for the UI. 

### 2. **Context Hub (Dynamic Expertise)**
The system is "Sector-Aware." Using a generic registry, it injects specialized **Expert Lenses** (e.g., Banking Specialist vs. IT Specialist) directly into the Agent's prompt based on the ticker being analyzed. 
* **Example:** When analyzing **HDFCBANK.NS**, the agent automatically prioritizes **Net Interest Margin (NIM)**, **CASA ratios**, and **Gross NPA** as per internal banking guidelines. 

### 3. **A2UI (Agent-to-UI) & Generative Frontend**
The frontend is reactive and generative. The Agent returns a structured **UI Payload** that commands the Streamlit interface to: 
* **Dynamic Banners:** Render color-coded alerts (Success/Warning/Error) based on detected risks. 
* **Metric Highlighting:** Automatically choose and display the 2-4 most critical metrics (e.g., isolating **Gross NPA** during a market anomaly). 

### 4. **Model Armor (Security & Compliance)**
A dedicated security layer that sits between the database and the LLM: 
* **Data Redaction:** Automatically masks PII and internal metadata before it reaches the model. 
* **Instruction Guardrails:** Ensures the model strictly adheres to official HDFC technical standards and formatting. 

---

## 🛠️ Tech Stack

* **Logic:** Python 3.11, LangGraph, asyncio. 
* **LLM:** Gemini 3 Flash (Paid Tier). 
* **Frontend:** Streamlit (Reactive Generative UI). 
* **Data:** PostgreSQL (via MCP), yfinance (Market History). 
* **Reporting:** FPDF (Automated Executive Briefings). 

---

## 📈 Demo Workflow

1.  **Selection:** User selects a "Banking Specialist" lens for HDFCBANK.NS. 
2.  **Reasoning:** The Agent "decides" to read Page 5 and 12 of the earnings transcript to find **NIM** and **NPA** figures. 
3.  **Visualization:** The dashboard renders a **HOLD** recommendation with a warning banner regarding management volatility. 
4.  **Export:** A one-click **Executive PDF** is generated, branded for internal use. 

---

## 👨‍💻 Developed By
**Himanshu Verma** 
*Senior GenAI Engineer, HDFC* 
*5.7+ Years Experience in Software Engineering* 


## 📁 Project Structure

```text
├── app.py                # Main Streamlit UI & Orchestration 
├── research_graph.py     # LangGraph State Machine & Agent Nodes 
├── page_index.py         # Vectorless PageIndex Researcher Logic 
├── process_document.py   # PDF Ingestion & Text Shredding 
├── expert_registry.py    # Context Hub for Sector-Aware Lenses 
├── mcp_finance_server.py # Postgres Connector (Model Context Protocol) 
├── model_armor.py        # Security Layer for Data Redaction & Guardrails 
├── report_generator.py   # FPDF logic for Executive Briefings 
├── vault_manager.py      # Local Knowledge Vault Management 
├── auditor_swarm.py      # Background monitoring & forensic reporting 
├── .env                  # API Keys (Git-Ignored) 
├── .gitignore            # Security Shield for Local Data & Secrets 
├── pyproject.toml        # Project Metadata & Dependencies 
└── chub_content/         # Local Knowledge Vault Storage