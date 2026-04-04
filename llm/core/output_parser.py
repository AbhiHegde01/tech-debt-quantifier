import json
import re

class OutputParser:
    @staticmethod
    def parse_json(raw_text):
        """
        Cleans the LLM output (removes markdown markers) 
        and parses it into a Python dictionary.
        """
        if not raw_text:
            return None

        # Look for JSON blocks specifically (e.g., ```json ... ```)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
        if json_match:
            raw_text = json_match.group(1)
        else:
            # Fallback for naked JSON strings wrapped in standard markdown (e.g., ``` ... ```)
            fallback_match = re.search(r'```\s*(\{.*?\})\s*```', raw_text, re.DOTALL)
            if fallback_match:
                raw_text = fallback_match.group(1)
            else:
                # Absolute fallback: just find the first { and last }
                curly_match = re.search(r'(\{.*\})', raw_text, re.DOTALL)
                if curly_match:
                    raw_text = curly_match.group(1)

        try:
            return json.loads(raw_text.strip())
        except json.JSONDecodeError as e:
            print(f"JSON Parsing Error: {e}")
            return {
                "error": "Invalid JSON format from LLM",
                "raw_text": raw_text[:200]
            }