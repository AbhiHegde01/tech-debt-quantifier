import os
import requests
from config import Config # This connects it to your config.py

class GeminiClient:
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        # This line now pulls directly from your Config class!
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.MODEL_ID}:generateContent?key={self.api_key}"
        
        if not self.api_key:
            print("❌ ERROR: GEMINI_API_KEY missing from .env")

    def generate_insight(self, system_prompt, user_prompt):
        headers = {'Content-Type': 'application/json'}
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"System Instructions: {system_prompt}\n\nUser Request: {user_prompt}"
                }]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": Config.TEMPERATURE
            }
        }
        
        try:
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            # This will print the EXACT url it's trying to hit so we can see it
            print(f"⚠️ Gemini API Error: {str(e)}")
            print(f"DEBUG: Attempted URL: {self.url.split('?')[0]}") 
            return None