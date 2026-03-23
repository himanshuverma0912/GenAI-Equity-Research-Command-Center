import fitz  # PyMuPDF
import os

def ingest_pdf_to_chub(pdf_path, ticker):
    doc = fitz.open(pdf_path)
    
    # --- RELATIVE PATH LOGIC ---
    # Finds the folder where THIS script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Builds the path to chub_content/documents/{ticker}
    base_dir = os.path.join(current_dir, "chub_content", "documents", ticker)
    os.makedirs(base_dir, exist_ok=True)
    
    page_map = {}
    for i, page in enumerate(doc):
        page_num = i + 1
        text = page.get_text() 
        
        # Capture 1500 chars for the Page Index search 
        # This ensures keywords like 'NIM' or 'NPA' are indexed
        summary_snippet = text[:1500].replace("\n", " ")
        page_map[f"page_{page_num}"] = summary_snippet
        
        # Save the full text for the Agent to read later using relative path
        page_file_path = os.path.join(base_dir, f"page_{page_num}.txt")
        with open(page_file_path, "w", encoding="utf-8") as f:
            f.write(text)
    
    print(f"✅ Ingested {len(doc)} pages for {ticker}")
    return page_map