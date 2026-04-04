import json
import os
import requests
import time

# --- CONFIG ---
API_KEY = "AIzaSyDUI-t-lIlYYpXZ2ILSwEHwFUdd9ZQmV_M" 
MODEL = "gemini-3-flash-preview" 
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
INPUT_FILE = "input.json"
OUTPUT_FILE = "advanced_output.json" # Saving to a new file so we don't overwrite the old one

def read_target_code(filepath):
    """Actually reads the code from the file so the AI isn't guessing."""
    if not filepath or not os.path.exists(filepath):
        return "// Source code file not found on disk."
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Grab the first 400 lines to give deep context without hitting token limits
            return "".join(f.readlines()[:400])
    except Exception as e:
        return f"// Error reading source code: {e}"

def get_deep_insight(issue, code_context):
    # The Elite Architect Prompt
    prompt = f"""
    Act as an Elite Software Architect and Business Analyst. 
    Analyze the following technical debt issue and the provided code context.
    
    Issue Description: {issue.get('description', 'Unknown')}
    Code Context:
    {code_context}
    
    You MUST return ONLY a raw JSON object with the following exact structure. Provide deep, analytical, and highly technical insights:
    {{
        "technical_debt_score": <int 1-10>,
        "remediation_cost_hours": <int estimated hours to fix>,
        "priority": "<high/med/low>",
        "improvement_areas": [
            "<specific code-level suggestion 1>",
            "<specific code-level suggestion 2>"
        ],
        "code_redundancies": "<Identify redundant logic and its structural flaw>",
        "business_impact": {{
            "time_loss_statistic": "<e.g., 'Adds estimated 15% overhead to sprint velocity due to brittle tests'>",
            "expense_impact": "<How this redundancy translates to wasted compute resources or developer cost>"
        }},
        "efficient_replacements": [
            "<Specific library, design pattern, or architecture to replace the current implementation>"
        ]
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json", "temperature": 0.2} # Kept low for highly factual/logical output
    }
    
    # 5-Try Retry logic remains to protect against rate limits
    for attempt in range(5):
        try:
            res = requests.post(URL, json=payload, timeout=60)
            res.raise_for_status()
            return res.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            if "429" in str(e):
                wait_time = (attempt + 1) * 15
                print(f"   🛑 Rate limited. Cooling down for {wait_time}s...")
                time.sleep(wait_time)
                continue
            elif ("503" in str(e) or "timeout" in str(e).lower()) and attempt < 4:
                print(f"   ⚠️ Server busy. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            print(f"   ❌ Final Error: {e}")
            return None

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found!")
        return

    with open(INPUT_FILE, "r") as f:
        data = json.load(f)
    
    issues = data.get("top_10_priority", [])
    print(f"🚀 FIRING UP ADVANCED ENGINE: Processing {len(issues)} issues...")
    
    results = []
    for i, issue in enumerate(issues):
        print(f"\n[{i+1}/{len(issues)}] Deep Scanning: {issue.get('id')}...")
        
        # We are actually reading the files now
        actual_code = read_target_code(issue.get('file'))
        
        insight_raw = get_deep_insight(issue, actual_code)
        
        if insight_raw:
            try:
                insight = json.loads(insight_raw)
                # Stitch the original data back in for frontend tracking
                insight["issue_id"] = issue.get("id")
                insight["file_scanned"] = issue.get("file")
                results.append(insight)
                print(f"   ✅ Advanced Insights Generated!")
            except json.JSONDecodeError:
                print(f"   ⚠️ AI returned malformed JSON.")
        
        if i < len(issues) - 1:
            print("   ⏳ Taking a 10s breather to respect API limits...")
            time.sleep(10)

    # Save to a new file so you can compare it to the basic one
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump({"llm_insights": results}, f, indent=4)
    
    print(f"\n🏆 PIPELINE COMPLETE! Check {OUTPUT_FILE}")

if __name__ == "__main__":
    main()