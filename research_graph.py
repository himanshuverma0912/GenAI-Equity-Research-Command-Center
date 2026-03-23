import os
import asyncio
import yfinance as yf
from textblob import TextBlob
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import json
# --- MCP & Context Hub Imports ---
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from expert_registry import ExpertiseRegistry

# 🔥 NEW: Import the Security Gateway
from model_armor import ModelArmor

registry = ExpertiseRegistry()
armor = ModelArmor() # Initialize Model Armor

from page_index import VectorlessPageIndex
indexer = VectorlessPageIndex()

# 1. Define the State
class EquityResearchState(TypedDict):
    ticker: str
    raw_data: str
    sentiment_data: str 
    analysis: str
    ui_payload: dict     # <-- NEW: The A2UI Instructions
    active_persona: str
    document_context: str

# 2. Initialize the LLM via LiteLLM Proxy
smart_llm = ChatOpenAI(
    base_url="http://127.0.0.1:4000",
    api_key="litellm-proxy", 
    model="complex-reasoning-model"
)

# 3. Define the Nodes

# ELITE FIX: The Data Gatherer is now an async MCP Client
async def data_gatherer_node(state: EquityResearchState):
    ticker_symbol = state['ticker']
    print(f"--> [Data Gatherer] Asking MCP Server for {ticker_symbol} metrics...")
    
    # Define how to launch the server (runs silently in the background)
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp_finance_server.py"],
    )
    
    try:
        # Open the connection to the MCP Server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Ask the server to run the tool we created
                response = await session.call_tool("get_equity_snapshot", arguments={"ticker": ticker_symbol})
                
                # Parse the response
                if response.content and len(response.content) > 0:
                    raw_financial_data = response.content[0].text
                else:
                    raw_financial_data = "Error: Blank response from MCP."
                    
    except Exception as e:
        raw_financial_data = f"MCP Connection Error: {str(e)}"
        
    return {"raw_data": raw_financial_data}

# Sentiment Node remains mostly the same, but LangGraph handles it easily alongside async nodes
def sentiment_analyzer_node(state: EquityResearchState):
    ticker_symbol = state['ticker']
    print(f"--> [Sentiment Analyzer] Scraping news for {ticker_symbol}...")
    
    try:
        stock = yf.Ticker(ticker_symbol)
        news = stock.news
        
        if not news:
            return {"sentiment_data": "No recent news found for this ticker."}
        
        headlines_text = ""
        total_polarity = 0
        count = 0
        
        for article in news[:5]:
            title = article.get('title') or article.get('content', {}).get('title')
            if title:
                analysis = TextBlob(title)
                total_polarity += analysis.sentiment.polarity
                headlines_text += f"- {title}\n"
                count += 1
            
        if count == 0:
            return {"sentiment_data": "News found, but headlines were unreadable. JSON structure may have changed."}

        avg_polarity = total_polarity / count
        emoji = "📈" if avg_polarity > 0.05 else "📉" if avg_polarity < -0.05 else "⚖️"
        sentiment_label = "Bullish" if avg_polarity > 0.05 else "Bearish" if avg_polarity < -0.05 else "Neutral"
        
        return {"sentiment_data": f"{emoji} **Score: {avg_polarity:.2f} ({sentiment_label})**\n\n{headlines_text}"}

    except Exception as e:
        return {"sentiment_data": f"Sentiment analysis failed: {str(e)}"}




async def document_researcher_node(state: EquityResearchState):
    ticker = state['ticker']
    print(f"--> [Document Researcher] Searching PageIndex for {ticker} documents...") # <--- ADD THIS
    
    # Identify focus
    focus = "NIM NPA CASA" if "BANK" in ticker else "Attrition Revenue"
    
    target_pages = indexer.get_relevant_pages(ticker, focus)
    print(f"--> [Document Researcher] Selected Pages: {target_pages}") # <--- ADD THIS
    
    context_bits = []
    for pg in target_pages:
        content = indexer.load_page_content(ticker, pg)
        if content:
            print(f"--> [Document Researcher] Successfully read {pg}") # <--- ADD THIS
            context_bits.append(f"--- DOCUMENT {pg.upper()} ---\n{content}")
    
    combined_docs = "\n\n".join(context_bits)
    return {"document_context": combined_docs}


async def financial_analyst_node(state: EquityResearchState):
    ticker = state['ticker']
    safe_raw_data = armor.shield_data(state['raw_data'])
    
    persona_id = state.get("persona_id") or registry.get_skill_id(ticker)
    persona_context = registry.fetch_resource(persona_id)
    tech_docs = registry.fetch_resource("openai/api-docs")
    
    # 🔥 THE A2UI SYSTEM PROMPT 🔥
    # 🔥 THE GENERIC AGENTIC SYSTEM PROMPT 🔥
    system_content = f"""
    ### YOUR ROLE & EXPERTISE:
    {persona_context}
    
    ### TECHNICAL STANDARDS:
    {tech_docs}
    
    ### TASK:
    Perform a deep-dive analysis of {ticker}. You are responsible for synthesizing raw database metrics with the 'UNSTRUCTURED CONTEXT' provided.

    ### EXTRACTION PROTOCOL:
    1. **Prioritize Evidence:** Scan the 'UNSTRUCTURED CONTEXT' for specific banking KPIs: Net Interest Margin (NIM), Non-Performing Assets (NPA), and Loan-to-Deposit Ratio (LDR) glide paths.
    2. **Quantitative Precision:** You MUST extract exact percentages, basis points, or ratios if they are mentioned. Do not summarize with "stable" or "improving" if a specific number like "3.4%" or "1.1%" is available.
    3. **Merger/Strategic Context:** Incorporate management's commentary on integration or strategic pivots found in the text.

    ### OUTPUT CONSTRAINTS:
    - Return ONLY a single, valid JSON object.
    - Ensure the 'key_metrics' array captures at least 3 discovered data points from the unstructured text.
    - If a metric is missing, use database values as a fallback, but mark the source in the 'thesis'.

    JSON Schema:
    {{
        "thesis": "2-paragraph analysis. Integrate extracted NIM/NPA figures and management outlook here.",
        "recommendation": "BUY | HOLD | SELL",
        "status": "success | warning | error",
        "key_metrics": [
            {{"label": "Metric Name", "value": "Found Value (e.g. 3.4%)"}}
        ]
    }}
    """

    human_content = f"""
    INTERNAL DATABASE RECORDS (Sanitized):
    {safe_raw_data}

    UNSTRUCTURED CONTEXT (From PageIndex):
    {state.get('document_context', 'No document data found.')}
    
    MARKET SENTIMENT & NEWS:
    {state.get('sentiment_data', 'No sentiment data available.')}
    """

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=human_content)
    ]
    
    response = await smart_llm.ainvoke(messages)
    
    # 🔥 A2UI PARSER: Convert the LLM's text into a Python Dictionary
    raw_output = response.content.strip()
    
    # Clean up markdown code blocks if the LLM ignores instructions and adds them
    if raw_output.startswith("```json"):
        raw_output = raw_output[7:-3].strip()
    elif raw_output.startswith("```"):
        raw_output = raw_output[3:-3].strip()
        
    try:
        parsed_payload = json.loads(raw_output)
        final_analysis = parsed_payload.get("thesis", "Thesis missing from payload.")
        ui_data = {
            "recommendation": parsed_payload.get("recommendation", "HOLD"),
            "status": parsed_payload.get("status", "success"),
            "key_metrics": parsed_payload.get("key_metrics", [])
        }
    except json.JSONDecodeError as e:
        print(f"❌ JSON Parsing Error: {e}")
        # Fallback if the LLM fails to output valid JSON
        final_analysis = raw_output 
        ui_data = {
            "recommendation": "UNKNOWN",
            "status": "warning",
            "key_metrics": []
        }
    
    return {
        "analysis": final_analysis, 
        "raw_data": safe_raw_data,
        "active_persona": persona_id,
        "ui_payload": ui_data # Send the UI instructions to Streamlit!
    }

# 4. Build and Compile the Graph (Updated Flow)
builder = StateGraph(EquityResearchState)

builder.add_node("gatherer", data_gatherer_node)
builder.add_node("researcher", document_researcher_node) # NEW
builder.add_node("sentiment", sentiment_analyzer_node)
builder.add_node("analyst", financial_analyst_node)

# NEW FLOW: Gatherer -> Sentiment -> Analyst
builder.add_edge(START, "gatherer")
builder.add_edge("gatherer", "researcher") # Inserted here
builder.add_edge("researcher", "sentiment")
builder.add_edge("sentiment", "analyst")
builder.add_edge("analyst", END)

graph = builder.compile()

# 5. Run the Graph (Now requires asyncio)
async def main():
    target_ticker = "HDFCBANK.NS" 
    print(f"Starting Elite MCP-Powered Research for: {target_ticker}\n" + "-"*40)
    
    initial_state = {"ticker": target_ticker, "raw_data": "", "sentiment_data": "", "analysis": ""}
    
    # Use ainvoke() to run the graph asynchronously
    final_state = await graph.ainvoke(initial_state)
    
    print("\n" + "="*40)
    print("INTERNAL DATABASE RECORDS EXTRACTED VIA MCP (SANITIZED):")
    print("="*40)
    print(final_state['raw_data'].strip())
    
    print("\n" + "="*40)
    print("FINAL INVESTMENT THESIS:")
    print("="*40)
    print(final_state['analysis'])

if __name__ == "__main__":
    # Execute the async loop
    asyncio.run(main())