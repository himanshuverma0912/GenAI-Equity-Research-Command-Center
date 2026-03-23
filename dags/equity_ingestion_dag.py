from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pendulum import datetime
import yfinance as yf
import logging
import tempfile
import os

# Setup logging for better visibility in Airflow UI
logger = logging.getLogger("airflow.task")

@dag(
    dag_id="daily_equity_ingestion",
    start_date=datetime(2026, 3, 1),
    schedule=None,
    catchup=False,
    tags=["finance", "genai", "elite-architecture"],
)
def equity_data_pipeline():

    @task
    def setup_database():
        """Ensures the PostgreSQL table exists before ingestion."""
        pg_hook = PostgresHook(postgres_conn_id='finance_db_conn')
        create_table_query = """
            CREATE TABLE IF NOT EXISTS equity_metrics (
                id SERIAL PRIMARY KEY,
                ticker VARCHAR(50) NOT NULL,
                current_price NUMERIC,
                market_cap NUMERIC,
                pe_ratio NUMERIC,
                summary TEXT,
                ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """
        pg_hook.run(create_table_query)
        logger.info("Database table 'equity_metrics' is ready.")

    @task
    def extract_market_data(ticker: str) -> dict:
        """
        Fetches data for a single ticker.
        Uses a temporary directory to prevent 'UNIQUE constraint' errors 
        and 'NoneType' errors in yfinance 2026.
        """
        logger.info(f"Starting extraction for {ticker}...")
        
        # Create a unique temporary directory for this specific task instance
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Tell yfinance to use this unique path for its cookie/cache database
            yf.set_tz_cache_location(tmp_dir)
            
            stock = yf.Ticker(ticker)
            
            try:
                # Trigger the network call
                info = stock.info
                
                # Validation: check if we got a real response
                if not info or len(info) <= 1:
                    logger.warning(f"No detailed info for {ticker}. Attempting fast_info fallback.")
                    return {
                        "ticker": ticker,
                        "current_price": getattr(stock.fast_info, 'last_price', None),
                        "market_cap": getattr(stock.fast_info, 'market_cap', None),
                        "pe_ratio": None,
                        "summary": "Data fetched via fast_info fallback."
                    }

                # Map the Yahoo Finance keys to our dictionary
                payload = {
                    "ticker": ticker,
                    "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                    "summary": info.get("longBusinessSummary", "N/A")[:500]
                }
                logger.info(f"Successfully extracted data for {ticker}")
                return payload

            except Exception as e:
                logger.error(f"Failed to extract {ticker}: {str(e)}")
                raise e

    @task
    def load_to_postgres(payload: dict):
        """Inserts a single ticker's data into the PostgreSQL database."""
        if not payload or not payload.get('ticker'):
            logger.warning("Empty payload received. Skipping insert.")
            return

        pg_hook = PostgresHook(postgres_conn_id='finance_db_conn')
        insert_query = """
            INSERT INTO equity_metrics (ticker, current_price, market_cap, pe_ratio, summary)
            VALUES (%s, %s, %s, %s, %s);
        """
        params = (
            payload['ticker'], 
            payload['current_price'], 
            payload['market_cap'], 
            payload['pe_ratio'], 
            payload['summary']
        )
        
        pg_hook.run(insert_query, parameters=params)
        logger.info(f"Loaded {payload['ticker']} into Postgres.")

    # --- Execution Flow ---
    
    # 1. Define the Watchlist
    watchlist = ["HDFCBANK.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "ICICIBANK.NS"]
    
    # 2. Initialize the DB
    setup_task = setup_database()
    
    # 3. Dynamic Task Mapping (Parallelism)
    # This spins up 5 separate 'extract' tasks in parallel
    extracted_data_list = extract_market_data.expand(ticker=watchlist)
    
    # 4. Dependency Mapping
    # Ensure DB is ready -> Extract Data -> Load Data
    setup_task >> extracted_data_list
    load_to_postgres.expand(payload=extracted_data_list)

# Instantiate the DAG
ingestion_dag = equity_data_pipeline()