import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class PromptBuilder:
    def __init__(self):
        self.prompts_dir = Config.PROMPTS_DIR

    def _read_file(self, filename):
        path = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(path): 
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def build_system_prompt(self):
        return self._read_file("architect_persona.txt")

    def build_user_prompt(self, issue, code_snippet):
        # Extracting the new rich data from your JSON contract
        tags = ", ".join(issue.get('tags', []))
        
        return f"""
        Analyze this Technical Debt issue from our codebase graph:
        
        - ID: {issue.get('id')}
        - TYPE: {issue.get('type')}
        - CATEGORY: {issue.get('category')}
        - SEVERITY: {issue.get('severity')}
        - EFFORT: {issue.get('effort')}
        - SYSTEM IMPACT SCORE: {issue.get('system_impact_score')}
        - BLAST RADIUS: {issue.get('blast_radius')} dependent modules
        - TAGS: {tags}
        - MODULE: {issue.get('module')}
        - FUNCTION: {issue.get('function')}
        - STATIC ANALYSIS IMPACT: {issue.get('impact')}

        SOURCE CODE:
        ```python
        {code_snippet}
        ```

        TASK:
        As a Senior Architect, provide a professional quantification.
        Focus heavily on the "Blast Radius" and "System Impact Score" to explain the "Debt Interest" (how much this slows down the team).
        
        RETURN JSON ONLY:
        {{
            "issue_id": "{issue.get('id')}",
            "explanation": "Technical root cause based on the code.",
            "business_impact": "Financial/Time cost explanation.",
            "fix_suggestion": "Actionable refactoring steps.",
            "estimated_time_saving": "e.g., '5 hours/month'",
            "confidence": 0.9
        }}
        """