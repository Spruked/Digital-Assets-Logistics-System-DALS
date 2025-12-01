"""
Watches for AI-injection (Copilot, etc.)
"""
from datetime import datetime

class Sentinel:
    def __init__(self):
        self.threats = []

    def scan(self, html: str) -> bool:
        triggers = ["github-copilot", "monaco-editor", "ai-suggestion",
                    "data-ai-", "data-copilot"]
        for t in triggers:
            if t in html.lower():
                self.threats.append({"time": datetime.utcnow().isoformat(), "trigger": t})
                return True
        return False