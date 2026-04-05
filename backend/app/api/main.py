from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import lizard

# Ensure the backend folder is in the Python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from backend.services.llm_service import LLMService
from backend.services.repo_service import RepoService

# Initialize the FastAPI application
app = FastAPI(
    title="Tech Debt Quantifier",
    description="API for quantifying technical debt using Gemini 3 Flash",
    version="1.0.0"
)

# CORS Middleware (Allows your frontend to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- EXPECTED INPUT SCHEMAS ---

class DebtRequest(BaseModel):
    """Schema for direct code block analysis"""
    issue_description: str
    code_context: str

class GitHubRequest(BaseModel):
    """Schema for GitHub repository analysis"""
    github_url: str

# --- INITIALIZE SERVICES ---
llm_engine = LLMService()

# --- API ENDPOINTS ---

@app.get("/")
def health_check():
    """Simple check to make sure the server is awake."""
    return {"status": "🚀 Tech Debt Engine is online! Go to /docs to test."}

@app.post("/analyze")
def analyze_debt(request: DebtRequest):
    """Analyzes a raw block of code sent directly to the API."""
    try:
        print(f"📥 Received raw analysis request for: {request.issue_description[:50]}...")
        result = llm_engine.quantify_debt(
            issue_description=request.issue_description,
            code_context=request.code_context
        )
        return result
    except Exception as e:
        print(f"❌ API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-repo")
def analyze_github_repo(request: GitHubRequest):
    """Downloads a public GitHub repo, runs Lizard analysis, and sends to Gemini."""
    repo_service = RepoService()
    
    try:
        # Step 1: Clone the Repo
        repo_service.clone_public_repo(request.github_url)

        print("🕸️ Mapping dependency graph...")
        dependency_map = repo_service.get_dependency_map()
        
        # Step 2: Get all files (THIS WAS MISSING!)
        all_files = repo_service.get_all_code_files()
        if not all_files:
            repo_service.cleanup()
            raise HTTPException(status_code=400, detail="No recognizable code files found in repo.")
            
        # Step 3: REAL STATIC ANALYSIS (Lizard)
        print("🔍 Running static analysis to find highest Cyclomatic Complexity...")
        worst_file = ""
        max_complexity = 0
        
        for file in all_files:
            try:
                # Lizard analyzes the file for cyclomatic complexity
                analysis = lizard.analyze_file(file)
                if analysis.average_cyclomatic_complexity > max_complexity:
                    max_complexity = analysis.average_cyclomatic_complexity
                    worst_file = file
            except Exception as e:
                continue # Skip files Lizard can't read
                
        worst_code = repo_service.read_file_content(worst_file)
        print(f"🚨 Target Acquired: {os.path.basename(worst_file)} with Complexity Score: {max_complexity}")
        
        # Step 4: Send the worst file to Gemini
        print(f"🤖 Sending largest file to AI: {os.path.basename(worst_file)}")
        ai_insights = llm_engine.quantify_debt(
            issue_description=f"Massive file detected in repo ({os.path.basename(worst_file)}). High cyclomatic complexity.",
            code_context=worst_code
        )
        
        # Step 5: Clean up and Return
        repo_service.cleanup()
        
        # Attach the new data to the final output
        ai_insights["analyzed_file"] = os.path.basename(worst_file)
        ai_insights["blast_radius"] = dependency_map
        ai_insights["static_metrics"] = {
            "worst_file": os.path.basename(worst_file),
            "cyclomatic_complexity_score": round(max_complexity, 2)
        }
        return ai_insights

    except Exception as e:
        repo_service.cleanup() # Always clean up the hard drive even if it crashes
        print(f"❌ Repo Analysis Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))