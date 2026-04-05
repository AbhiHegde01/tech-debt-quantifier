import json
import requests
import time
import os
import re

class LLMService:
    def __init__(self):
        # First tries to get the key from Render's secure Environment Variables.
        # If it's running locally and can't find it, it falls back to your hardcoded key.
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            self.api_key = "AIzaSyDUI-t-lIlYYpXZ2ILSwEHwFUdd9ZQmV_M" 
            
        self.model = "gemini-3-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def quantify_debt(self, issue_description: str, code_context: str) -> dict:
        """Takes raw debt data and asks Gemini for business-level quantification."""
        
        # ONE unified, cleanly formatted prompt string
        prompt = f"""
        Act as an Elite Software Architect. Analyze this technical debt:
        
        Issue: {issue_description}
        
        Code Context:
        {code_context}
        
        You MUST return your analysis as a raw, valid JSON object. Do not wrap it in markdown blockquotes (```json). 
        You MUST use these exact keys:
        {{
            "technical_debt_score": <integer from 1 to 10>,
            "remediation_cost_hours": <integer estimating hours to fix>,
            "priority": "<string: Low, Medium, High, or Critical>",
            "business_impact": {{
                "expense": "<string describing cost impact>"
            }},
            "improvement_areas": [
                "<string area 1>",
                "<string area 2>"
            ],
            "efficient_replacements": [
                "<string replacement 1>",
                "<string replacement 2>"
            ]
        }}
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json", 
                "temperature": 0.2
            }
        }
        
        for attempt in range(3):
            try:
                res = requests.post(self.url, json=payload, timeout=60)
                res.raise_for_status()
                
                # Get the raw text from the AI
                raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
                
                # Strip out any accidental markdown ticks just to be safe
                clean_json = re.sub(r'```json\n|```', '', raw_text).strip()
                
                # Parse it into a real Python dictionary
                return json.loads(clean_json)
                
            except Exception as e:
                print(f"⚠️ API Attempt {attempt + 1} failed: {e}")
                if "429" in str(e) or "503" in str(e):
                    time.sleep(5)
                    continue
                # If it completely fails, return a safe fallback so the frontend doesn't crash
                return {
                    "error": str(e), 
                    "technical_debt_score": "?",
                    "remediation_cost_hours": "?",
                    "priority": "Error"
                }
        
        return {}