import json
import requests
import os

class LLMService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDUI-t-lIlYYpXZ2ILSwEHwFUdd9ZQmV_M")
        self.model = "gemini-1.5-flash"
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
            print("🤖 Sending request to Google Gemini API...")
            res = requests.post(
                self.url,
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1}
                },
                timeout=45
            )
            
            # If Google rejects the API key, catch it here
            if res.status_code != 200:
                print(f"❌ Gemini API Error: {res.text}")
                return self._fallback(f"API Error: {res.status_code}. Check Render Logs.")

            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            print(f"📥 Raw AI Response received! Length: {len(raw_text)} chars")
            
            # Indestructible JSON extractor
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            
            if start != -1 and end != -1:
                data = json.loads(raw_text[start:end+1])
                return data
            else:
                print("❌ No JSON brackets found in AI response.")
                return self._fallback("AI returned text instead of JSON.")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parse Error: {e}")
            return self._fallback("AI generated invalid JSON formatting.")
        except Exception as e:
            print(f"❌ Python Crash in LLM Service: {str(e)}")
            return self._fallback(f"Backend Crash: {str(e)}")

    def _fallback(self, reason: str) -> dict:
        """If ANYTHING fails, this guarantees the UI gets data instead of crashing."""
        return {
            "technical_debt_score": 0,
            "remediation_cost_hours": 0,
            "priority": "ERROR",
            "business_impact": {"expense": reason},
            "improvement_areas": ["Check the Render Logs to see the exact Python crash."],
            "efficient_replacements": ["Verify your GEMINI_API_KEY environment variable."]
        }