import os
import json
class VectorlessPageIndex:
    # In page_index.py
    def __init__(self):
        # Dynamically find the project root
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.SKILLS_BASE_DIR = os.path.join(self.BASE_DIR, "chub_content")
        # Path to the master_index.json
        self.INDEX_PATH = os.path.join(self.SKILLS_BASE_DIR, "documents", "master_index.json")
        
        if os.path.exists(self.INDEX_PATH):
            with open(self.INDEX_PATH, "r") as f:
                self.master_maps = json.load(f)
        else:
            self.master_maps = {}

    def get_relevant_pages(self, ticker, query_focus):
        map_data = self.master_maps.get(ticker, {})
        selected_pages = []
    
        # Banking specific keywords to look for in summaries
        banking_targets = ["nim", "margin", "npa", "asset quality", "glide path", "ldr", "casa"]
    
        for page, summary in map_data.items():
            # Check if page is a known financial summary page (usually 5-12) or contains keywords
            page_num = int(page.split('_')[1])
            if any(term in summary.lower() for term in banking_targets) or (5 <= page_num <= 12):
                selected_pages.append(page)
            
        # Always ensure Page 1 is there for context
        if "page_1" not in selected_pages:
            selected_pages.insert(0, "page_1")
        
        return selected_pages[:8] # Return up to 8 pages for analysis

    def load_page_content(self, ticker, page_id):
        """Fetch actual text from the 'vault' on disk with encoding safety."""
        path = os.path.join(self.SKILLS_BASE_DIR, "documents", ticker, f"{page_id}.txt")
        
        if os.path.exists(path):
            # Try UTF-8 first
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                # Fallback for Windows PowerShell 'echo' files (UTF-16)
                try:
                    with open(path, "r", encoding="utf-16") as f:
                        return f.read()
                except Exception as e:
                    return f"Error decoding file {page_id}: {str(e)}"
        return ""