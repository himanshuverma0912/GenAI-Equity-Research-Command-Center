import os
import time
import json
from process_document import ingest_pdf_to_chub

# --- RELATIVE PATH LOGIC ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WATCH_DIR = os.path.join(BASE_DIR, "raw_uploads")
DEST_DIR = os.path.join(BASE_DIR, "chub_content", "documents")
ARCHIVE_DIR = os.path.join(WATCH_DIR, "archived")

def start_vault_watcher():
    # Ensure all directories exist relatively
    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(DEST_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    print(f"👀 Vault Watcher Active: Monitoring {WATCH_DIR}...")
    
    while True:
        # Check for new PDFs
        files = [f for f in os.listdir(WATCH_DIR) if f.endswith(".pdf")]
        
        for file in files:
            # Assumes file name like HDFCBANK_Report.pdf
            ticker = file.split("_")[0] 
            pdf_path = os.path.join(WATCH_DIR, file)
            
            print(f"📂 New Document Detected: {file}. Processing for {ticker}...")
            
            # 1. Run your ingestion code
            page_map = ingest_pdf_to_chub(pdf_path, ticker)
            
            # 2. Update the Master Index relatively
            index_path = os.path.join(DEST_DIR, "master_index.json")
            existing_index = {}
            if os.path.exists(index_path):
                with open(index_path, "r") as f:
                    existing_index = json.load(f)
            
            existing_index[ticker] = page_map
            
            # 🔥 FIX: Changed mode from "r" to "w" to properly save the index
            with open(index_path, "w") as f:
                json.dump(existing_index, f, indent=4)
                
            # 3. Move the processed file to an 'archive' relative directory
            os.rename(pdf_path, os.path.join(ARCHIVE_DIR, file))
            print(f"✅ {ticker} is now indexed and live in the Swarm.")
            
        time.sleep(5) # Check every 5 seconds