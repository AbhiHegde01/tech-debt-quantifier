import json
import os
import sys

# Ensure the script can find the internal modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.llm_engine import LLMEngine
from config import Config

def main():
    input_path = Config.INPUT_FILE
    output_path = Config.OUTPUT_FILE
    
    if not os.path.exists(input_path):
        print(f"❌ Error: {input_path} not found. Check your tech-debt-quantifier root folder.")
        return

    # Load the prioritized issues list
    with open(input_path, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # UPDATED: No more Bedrock!
    print("🛰️  Initializing Gemini 1.5 Flash Engine...") 
    engine = LLMEngine()
    
    # Process the issues through Gemini
    output = engine.run(input_data)

    # Save the finalized insights to output.json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)
    
    print(f"✅ Success! Analysis saved to {output_path}")

if __name__ == "__main__":
    main()