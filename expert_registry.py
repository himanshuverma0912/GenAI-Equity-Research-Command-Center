import subprocess
import os

class ExpertiseRegistry:
    def __init__(self):
        # 1. This is the "Bridge" that the Streamlit dropdown uses
        self.registry_map = {
            "Value Investor": "finance/value-investor",
            "Aggressive Trader": "finance/aggressive-trader",
            "Banking Specialist": "skills/indian-banking",
            "IT Specialist": "skills/it-services"
        }
        
        # 2. Paths for Windows stability
        self.CHUB_PATH = r"C:\Users\Smily\AppData\Roaming\npm\chub.cmd"
        self.SKILLS_BASE_DIR = r"E:\equity-research-agent\chub_content"
        
        # 3. Keyword map for Auto-Routing
        self.sector_keywords = {
            "BANK": "skills/indian-banking",
            "HDFC": "skills/indian-banking",
            "TCS": "skills/it-services",
            "INFY": "skills/it-services"
        }

    def fetch_resource(self, resource_id: str):
        """Generic fetcher for any Chub resource (Persona or Tech Doc)."""
        # Try local file first (fastest)
        # Translates 'skills/it-services' -> 'E:\...\chub_content\skills\it-services\SKILL.md'
        local_path = os.path.join(self.SKILLS_BASE_DIR, resource_id.replace("/", os.sep), "SKILL.md")
        
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    return self._clean_expert_content(f.read())
            except Exception as e:
                return f"Error reading local file: {e}"

        # Fallback to CLI
        try:
            result = subprocess.run(
                [self.CHUB_PATH, "get", resource_id], 
                capture_output=True, text=True, timeout=5, shell=True
            )
            if result.returncode == 0:
                return self._clean_expert_content(result.stdout)
        except:
            pass
            
        return f"Resource {resource_id} not found in Hub."

    def get_skill_id(self, ticker: str):
        """Auto-detects sector from ticker name."""
        t = ticker.upper()
        for key, path in self.sector_keywords.items():
            if key in t:
                return path
        return "skills/macro-strategy"

    def get_skill_context(self, ticker: str):
        """Helper for simple lookups."""
        skill_id = self.get_skill_id(ticker)
        return self.fetch_resource(skill_id)

    def _clean_expert_content(self, text):
        """Standard cleaning for Chub metadata."""
        if "After using this doc" in text:
            text = text.split("After using this doc")[0]
        if "---" in text:
            parts = text.split("---")
            text = parts[2] if len(parts) >= 3 else parts[-1]
        return text.strip()