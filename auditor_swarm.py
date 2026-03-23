import asyncio
import re
from research_graph import graph
from expert_registry import ExpertiseRegistry
from mcp_finance_server import get_equity_snapshot, get_all_tickers 

# --- CONFIG ---
VOLATILITY_THRESHOLD = -1.5  # Trigger if price drops > 1.5%
CHECK_INTERVAL = 30          # Check every 30 seconds for the demo

async def monitor_portfolio():
    registry = ExpertiseRegistry()
    print("🚀 [Auditor Swarm] Autonomous Monitoring Active...")
    last_prices = {}

    while True:
        try:
            # 1. DYNAMIC FETCH: Get every ticker in your Postgres Watchlist
            watchlist = await get_all_tickers() 
            
            for ticker in watchlist:
                # 2. Fetch current data via MCP Logic
                raw_data = await get_equity_snapshot(ticker)
                
                # 3. Parse Price (Regex)
                price_match = re.search(r"Current Price: INR ([\d\.]+)", raw_data)
                if not price_match: continue
                current_price = float(price_match.group(1))
                
                # First run init
                if ticker not in last_prices:
                    last_prices[ticker] = current_price
                    print(f"📡 Now guarding: {ticker} @ ₹{current_price}")
                    continue

                # 4. ANOMALY DETECTION
                change = ((current_price - last_prices[ticker]) / last_prices[ticker]) * 100
                
                if change <= VOLATILITY_THRESHOLD:
                    print(f"\n⚠️  CRITICAL ALERT: {ticker} dropped {change:.2f}%!")
                    print(f"🧠 Activating Swarm with {ticker} Identity...")

                    # 5. TRIGGER BRAIN (LangGraph)
                    # This will automatically pull the NIM/Attrition rules from your Hub
                    initial_state = {
                        "ticker": ticker, 
                        "raw_data": raw_data, 
                        "sentiment_data": "", 
                        "analysis": ""
                    }
                    
                    result = await graph.ainvoke(initial_state)
                    
                    print(f"✅ THESIS GENERATED FOR {ticker}:")
                    print("-" * 50)
                    print(result['analysis'])
                    print("-" * 50 + "\n")
                
                last_prices[ticker] = current_price
                
        except Exception as e:
            print(f"❌ Auditor Swarm Error: {e}")
            
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(monitor_portfolio())