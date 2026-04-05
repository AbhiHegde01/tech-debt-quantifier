import json
import requests
import time

class LLMService:
    def __init__(self):
        # Your hardcoded 2026 key for the win
        self.api_key = "AIzaSyDUI-t-lIlYYpXZ2ILSwEHwFUdd9ZQmV_M" 
        self.model = "gemini-3-flash-preview"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def quantify_debt(self, issue_description: str, code_context: str) -> dict:
        """Takes raw debt data and asks Gemini for business-level quantification."""
        prompt = f"""
        Act as an Elite Software Architect. Analyze this technical debt:
        Issue: {issue_description}
        Code:
        {code_context}
        
        Return ONLY JSON:
        {{
            "technical_debt_score": 1-10,
            "remediation_cost_hours": 5,
            "priority": "high",
            "improvement_areas": ["suggestion"],
            "business_impact": {{"time_loss": "...", "expense": "..."}},
            "efficient_replacements": ["pattern"]
        }}
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json", "temperature": 0.2}
        }
        
        for attempt in range(3):
            try:
                res = requests.post(self.url, json=payload, timeout=60)
                res.raise_for_status()
                return json.loads(res.json()['candidates'][0]['content']['parts'][0]['text'])
            except Exception as e:
                if "429" in str(e) or "503" in str(e):
                    time.sleep(5)
                    continue
                return {"error": str(e), "technical_debt_score": 0}