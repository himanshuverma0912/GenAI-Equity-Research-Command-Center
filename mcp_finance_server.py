from mcp.server.fastmcp import FastMCP
import psycopg2
from psycopg2.extras import DictCursor
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# 1. Initialize the MCP Server
mcp = FastMCP("EliteFinanceServer")

def get_db_connection():
    """Helper to maintain consistency across tools."""
    return psycopg2.connect(
        dbname="airflow",
        user="airflow",
        password="airflow",
        host="127.0.0.1",
        port="5435"
    )

@mcp.tool()
async def get_all_tickers() -> list:
    """Fetches the unique list of all tickers currently in the HDFC Watchlist."""
    logger.info("Auditor Swarm requested full watchlist.")
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT ticker FROM equity_metrics;")
            rows = cur.fetchall()
            return [row[0] for row in rows]
    except Exception as e:
        logger.error(f"DB Error in get_all_tickers: {e}")
        return []
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@mcp.tool()
async def get_equity_snapshot(ticker: str) -> str:
    """Fetches the latest financial metrics for a given ticker from the internal PostgreSQL database."""
    logger.info(f"Agent requested data for ticker: {ticker}")
    
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT current_price, market_cap, pe_ratio, summary, ingestion_timestamp 
                FROM equity_metrics 
                WHERE ticker = %s 
                ORDER BY ingestion_timestamp DESC LIMIT 1;
            """
            cur.execute(query, (ticker.upper(),))
            row = cur.fetchone()
            
        if row:
            return (f"Ticker: {ticker.upper()}\n"
                    f"Current Price: INR {row['current_price']}\n"
                    f"Market Cap: INR {row['market_cap']}\n"
                    f"P/E Ratio: {row['pe_ratio']}\n"
                    f"Business Summary: {row['summary']}\n"
                    f"Internal Data As Of: {row['ingestion_timestamp']}")
        
        return f"No internal data found for {ticker.upper()}."
        
    except Exception as e:
        logger.error(f"Database Error: {str(e)}")
        return f"Database Error: {str(e)}"
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    mcp.run(transport="stdio")