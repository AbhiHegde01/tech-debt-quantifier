import json
import requests
import os

class LLMService:
    def __init__(self):
        # 1. Safely grab the API key. If Render has an empty string, fallback to your hardcoded one.
        key = os.environ.get("GEMINI_API_KEY", "").strip()
        self.api_key = key if key else "AIzaSyDUI-t-lIlYYpXZ2ILSwEHwFUdd9ZQmV_M"
        
        # 2. UPGRADE TO 2.0: The 404 error means the old 1.5 alias isn't routing correctly
        self.model = "gemini-2.0-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def quantify_debt(self, issue_description: str, code_context: str) -> dict:
        prompt = f"""
        Analyze this codebase:
        {code_context[:2000]}
        
        Return ONLY valid JSON. No markdown blockquotes. Use exactly these keys:
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
            print(f"🤖 Sending request to Google Gemini API ({self.model})...")
            res = requests.post(
                self.url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                },
                headers={"Content-Type": "application/json"},
                timeout=45
            )
            
            # If Google rejects the API request, pipe the EXACT Google error text to the UI
            if res.status_code != 200:
                error_msg = res.json().get("error", {}).get("message", "Unknown Error")
                print(f"❌ Gemini API Error {res.status_code}: {error_msg}")
                return self._fallback(f"Google API {res.status_code}: {error_msg}")

            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Indestructible JSON extractor
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            
            if start != -1 and end != -1:
                data = json.loads(raw_text[start:end+1])
                return data
            else:
                return self._fallback("AI returned text instead of JSON.")
                
        except json.JSONDecodeError as e:
            return self._fallback("AI generated invalid JSON formatting.")
        except Exception as e:
            return self._fallback(f"Backend Crash: {str(e)}")

    def _fallback(self, reason: str) -> dict:
        return {
            "technical_debt_score": 0,
            "remediation_cost_hours": 0,
            "priority": "ERROR",
            "business_impact": {"expense": reason},
            "improvement_areas": ["Check Render logs for the full trace."],
            "efficient_replacements": ["Verify your GEMINI_API_KEY environment variable is valid."]
        }