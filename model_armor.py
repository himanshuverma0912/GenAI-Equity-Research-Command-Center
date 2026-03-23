import re

class ModelArmor:
    """The Security Gateway for HDFC's GenAI Swarm."""
    
    def __init__(self):
        # Dictionary of patterns to intercept and mask
        self.patterns = {
            # Catches SQL timestamps (e.g., 2024-10-27 14:30:00.12345)
            "REDACTED_INTERNAL_TIMESTAMP": r"\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}(?:\.\d+)?",
            
            # Catches IP addresses (e.g., 127.0.0.1)
            "REDACTED_INTERNAL_IP": r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        }

    def shield_data(self, text: str) -> str:
        """Scrubs sensitive internal metadata before it hits the Cloud LLM."""
        safe_text = str(text)
        for label, pattern in self.patterns.items():
            safe_text = re.sub(pattern, f"[{label}]", safe_text)
        return safe_text