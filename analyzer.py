import os
import json
import uuid
import re

class TechDebtAnalyzer:
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.debt_issues = []
        # Debt markers we are looking for in the code
        self.markers = [r"TODO", r"FIXME", r"HACK", r"OPTIMIZE"]

    def scan_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # Rule 1: File is too long (God Object anti-pattern)
                if len(lines) > 300:
                    self.debt_issues.append({
                        "id": str(uuid.uuid4()),
                        "description": f"Excessive file length ({len(lines)} lines). Potential 'God Object' violating Single Responsibility Principle.",
                        "file": filepath
                    })

                # Rule 2: Search for explicit debt markers
                for line_num, line in enumerate(lines):
                    for marker in self.markers:
                        if re.search(marker, line, re.IGNORECASE):
                            self.debt_issues.append({
                                "id": str(uuid.uuid4()),
                                "description": f"Explicit debt marker found ({marker}) at line {line_num + 1}: {line.strip()}",
                                "file": filepath
                            })
                            
        except Exception as e:
            pass # Skip unreadable files (binary, compiled, etc.)

    def analyze(self):
        print(f"🔍 Scanning directory: {self.target_dir}...")
        for root, dirs, files in os.walk(self.target_dir):
            # Skip hidden folders and environments
            if '.git' in root or '__pycache__' in root or 'venv' in root:
                continue
                
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp')):
                    self.scan_file(os.path.join(root, file))

    def generate_input_json(self, output_path="input.json"):
        # We only want the top 10 to feed to Gemini
        top_10 = self.debt_issues[:10]
        
        output_data = {
            "top_10_priority": top_10
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4)
        
        print(f"✅ Found {len(self.debt_issues)} total issues.")
        print(f"✅ Packaged the top {len(top_10)} into {output_path} for LLM quantification.")


if __name__ == "__main__":
    # Point this at your own project folder to test it!
    # '.' means current directory
    target_project = "." 
    
    analyzer = TechDebtAnalyzer(target_project)
    analyzer.analyze()
    analyzer.generate_input_json()