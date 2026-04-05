import json
import requests
import os
import re

class LLMService:
    def __init__(self):
        # Grabs the key from Render. (Make sure your Render Environment Variable is exactly GEMINI_API_KEY)
        self.api_key = os.environ.get("GEMINI_API_KEY") 
        self.model = "gemini-1.5-flash"
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def quantify_debt(self, issue_description: str, code_context: str) -> dict:
        prompt = f"""
        Analyze this technical debt:
        Issue: {issue_description}
        Code Context: {code_context[:3000]}
        
        Return ONLY a raw JSON object. Do not include any explanations or markdown formatting. Use these exact keys:
        {{
            "technical_debt_score": <integer from 1 to 10>,
            "remediation_cost_hours": <integer>,
            "priority": "<string: Low, Medium, High, or Critical>",
            "business_impact": {{
                "expense": "<string>"
            }},
            "improvement_areas": [
                "<string>",
                "<string>"
            ],
            "efficient_replacements": [
                "<string>"
            ]
        }}
        """
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "response_mime_type": "application/json", # THIS forces Google's servers to only output JSON
                "temperature": 0.1
            }
        }

        try:
            res = requests.post(self.url, json=payload, timeout=60)
            
            # If Google rejects the request (e.g., bad API key), catch it immediately
            if res.status_code != 200:
                error_data = res.json().get('error', {}).get('message', 'Unknown API Error')
                return self._error_response(f"Google API Error: {res.status_code} - {error_data}")

            # Extract the text
            raw_text = res.json()['candidates'][0]['content']['parts'][0]['text']
            
            # Clean and parse it
            clean_json = re.sub(r'```json\n|```', '', raw_text).strip()
            return json.loads(clean_json)

        except json.JSONDecodeError as e:
            return self._error_response(f"AI returned broken JSON. Parse Error: {str(e)}. Raw AI Text: {raw_text}")
        except Exception as e:
            return self._error_response(f"Server execution error: {str(e)}")

    def _error_response(self, error_message: str) -> dict:
        """Pipes the actual error directly to the Streamlit UI so we can debug it."""
        return {
            "technical_debt_score": 0,
            "remediation_cost_hours": 0,
            "priority": "CRITICAL ERROR",
            "business_impact": {"expense": error_message},
            "improvement_areas": ["Check the Business Impact box above for the exact error log."],
            "efficient_replacements": ["Verify your GEMINI_API_KEY inside Render's Environment Variables."]
        }