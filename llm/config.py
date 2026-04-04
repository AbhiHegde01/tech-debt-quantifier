import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    # --- Gemini API Settings ---
    # Fetched from your .env file
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Using Gemini 1.5 Flash - optimized for speed and high-volume code analysis
    MODEL_ID = "gemini-1.5-flash"
    
    # Base URL for the Google AI Studio API
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent"

    # --- Inference Parameters ---
    TEMPERATURE = 0.2
    MAX_TOKENS = 2500
    TOP_P = 0.9

    # --- Path Resolution (Windows/Linux Compatible) ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

    # --- File System Paths (Input/Output) ---
    # These point to your master files in the tech-debt-quantifier root folder
    INPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "input.json"))
    OUTPUT_FILE = os.path.abspath(os.path.join(BASE_DIR, "..", "output.json"))