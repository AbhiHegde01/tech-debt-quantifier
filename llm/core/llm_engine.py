import json
import os
from clients.gemini_client import GeminiClient
from core.prompt_builder import PromptBuilder
from core.output_parser import OutputParser

class LLMEngine:
    def __init__(self):
        print("🛰️ Initializing Gemini 1.5 Flash Engine...")
        self.client = GeminiClient()
        self.builder = PromptBuilder()
        self.parser = OutputParser()

    def _read_actual_code(self, file_path):
        """Attempts to read the source code from the project root."""
        # Adjusting path to look for source code relative to the llm folder
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", file_path))
        try:
            if os.path.exists(root_path):
                with open(root_path, "r", encoding="utf-8") as f:
                    # Keep within token limits by taking the first 500 lines
                    return "".join(f.readlines()[:500]) 
            return f"// Source code for {file_path} not found on disk."
        except Exception as e:
            return f"// Error reading file: {str(e)}"

    def run(self, input_data):
        system_prompt = self.builder.build_system_prompt()
        results = []

        # Target the top 10 priority issues as defined in input.json
        issues = input_data.get("top_10_priority", [])
        print(f"📊 Processing {len(issues)} priority issues...")
        
        for issue in issues:
            issue_id = issue.get('id')
            print(f"🚀 Quantifying Issue: {issue_id}...")
            
            # Pulling actual code context for the AI to analyze
            code_context = self._read_actual_code(issue.get('file'))
            user_prompt = self.builder.build_user_prompt(issue, code_context)
            
            # Making the call to Gemini
            raw_response = self.client.generate_insight(system_prompt, user_prompt)
            
            # Parsing the AI's JSON response
            insight = self.parser.parse_json(raw_response)
            
            if insight:
                if "issue_id" not in insight:
                    insight["issue_id"] = issue_id
                results.append(insight)
            else:
                # If Gemini fails, we store a null so the output structure stays consistent
                results.append(None)

        return {"llm_insights": results}