import json
import requests
import os

class LLMService:
    def __init__(self):
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.api_key = key if key else "AIzaSyDUI-t-lIlYYpXZ2ILSwEHwFUdd9ZQmV_M"
        # THE FIX: Google requires the "-latest" tag to not throw a 404
        self.model = "gemini-1.5-flash-latest" 
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def quantify_debt(self, issue_description: str, code_context: str) -> dict:
        prompt = f"""
        Analyze this codebase: {code_context[:2000]}
        
        Return ONLY valid JSON. No markdown. Use exactly these keys:
        {{
            "technical_debt_score": 8,
            "remediation_cost_hours": 10,
            "priority": "High",
            "business_impact": {{"expense": "High cost"}},
            "improvement_areas": ["Fix X"],
            "efficient_replacements": ["Use Y"]
        }}
        """
        
        try:
            res = requests.post(
                self.url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                headers={"Content-Type": "application/json"},
                timeout=45
            )
            
            if res.status_code != 200:
                return self._fallback(f"Google API Error {res.status_code}: {res.text}")

            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            
            if start != -1 and end != -1:
                return json.loads(raw_text[start:end+1])
            return self._fallback("AI returned text, not JSON.")
                
        except Exception as e:
            return self._fallback(f"Server Crash: {str(e)}")

    def _fallback(self, reason: str) -> dict:
        return {
            "technical_debt_score": 0,
            "remediation_cost_hours": 0,
            "priority": "ERROR",
            "business_impact": {"expense": reason},
            "improvement_areas": ["Check the reason above."],
            "efficient_replacements": ["Verify your API key and model."]
        }