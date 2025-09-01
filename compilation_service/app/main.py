from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .sandbox import run_in_sandbox

app = FastAPI()

class CompilationRequest(BaseModel):
    source_code: str

# This is your existing endpoint for compiling code. It remains unchanged.
@app.post("/compile")
async def compile_code(request: CompilationRequest):
    """
    Receives a compilation request and executes it in the sandbox.
    """
    if not request.source_code.strip():
        raise HTTPException(status_code=400, detail="source_code cannot be empty.")
    
    return await run_in_sandbox(request.source_code)


# --- NEW: Health Check Endpoint ---
# This gives Render a URL to check if the service is alive.
@app.get("/")
async def health_check():
    """
    A simple endpoint to confirm the service is running.
    """
    return {"status": "ok", "message": "Compilation service is healthy."}
