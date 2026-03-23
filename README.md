# 🏦 GenAI Equity Research Command Center

An enterprise-grade, agentic workstation designed to automate deep-dive equity research. [cite_start]This system synthesizes structured SQL data, unstructured financial transcripts, and live market sentiment into actionable, branded executive briefings. [cite: 4, 10, 15]

## 🚀 Key Architectural Pillars

### 1. **The Swarm (Multi-Agent Orchestration)**
[cite_start]Powered by **LangGraph**, the system utilizes a specialized swarm of agents to ensure separation of concerns and high-fidelity reasoning: [cite: 12]
* [cite_start]**Data Gatherer:** Securely fetches internal metrics (P/E, Market Cap) from a PostgreSQL database via **MCP (Model Context Protocol)**. [cite: 11]
* [cite_start]**Document Researcher:** Employs a **Vectorless PageIndex** to reason over which specific pages of an earnings call or annual report to read, avoiding the noise of traditional Vector RAG. [cite: 15]
* [cite_start]**Sentiment Analyzer:** Scrapes live news to quantify market mood using NLP. [cite: 12]
* [cite_start]**Financial Analyst:** The core engine that synthesizes all inputs into a structured JSON payload for the UI. [cite: 14]

### 2. **Context Hub (Dynamic Expertise)**
The system is "Sector-Aware." [cite_start]Using a generic registry, it injects specialized **Expert Lenses** (e.g., Banking Specialist vs. IT Specialist) directly into the Agent's prompt based on the ticker being analyzed. [cite: 13, 15]
* [cite_start]**Example:** When analyzing **HDFCBANK.NS**, the agent automatically prioritizes **Net Interest Margin (NIM)**, **CASA ratios**, and **Gross NPA** as per internal banking guidelines. [cite: 13, 25]

### 3. **A2UI (Agent-to-UI) & Generative Frontend**
The frontend is reactive and generative. [cite_start]The Agent returns a structured **UI Payload** that commands the Streamlit interface to: [cite: 14]
* [cite_start]**Dynamic Banners:** Render color-coded alerts (Success/Warning/Error) based on detected risks. [cite: 14]
* [cite_start]**Metric Highlighting:** Automatically choose and display the 2-4 most critical metrics (e.g., isolating **Gross NPA** during a market anomaly). [cite: 14]

### 4. **Model Armor (Security & Compliance)**
[cite_start]A dedicated security layer that sits between the database and the LLM: [cite: 15]
* [cite_start]**Data Redaction:** Automatically masks PII and internal metadata before it reaches the model. [cite: 15]
* [cite_start]**Instruction Guardrails:** Ensures the model strictly adheres to official HDFC technical standards and formatting. [cite: 15]

---

## 🛠️ Tech Stack

* [cite_start]**Logic:** Python 3.11, LangGraph, asyncio. [cite: 12]
* [cite_start]**LLM:** Gemini 3 Flash (Paid Tier). [cite: 4, 12]
* [cite_start]**Frontend:** Streamlit (Reactive Generative UI). [cite: 14]
* [cite_start]**Data:** PostgreSQL (via MCP), yfinance (Market History). [cite: 11]
* [cite_start]**Reporting:** FPDF (Automated Executive Briefings). [cite: 16]

---

## 📈 Demo Workflow

1.  [cite_start]**Selection:** User selects a "Banking Specialist" lens for HDFCBANK.NS. [cite: 13]
2.  [cite_start]**Reasoning:** The Agent "decides" to read Page 5 and 12 of the earnings transcript to find **NIM** and **NPA** figures. [cite: 15]
3.  [cite_start]**Visualization:** The dashboard renders a **HOLD** recommendation with a warning banner regarding management volatility. [cite: 14, 21]
4.  [cite_start]**Export:** A one-click **Executive PDF** is generated, branded for internal use. [cite: 16, 22]

---

## 👨‍💻 Developed By
[cite_start]**Himanshu Verma** [cite: 1, 2]
[cite_start]*Senior GenAI Engineer, HDFC* [cite: 3]
[cite_start]*5.7+ Years Experience in Software Engineering* [cite: 2]


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