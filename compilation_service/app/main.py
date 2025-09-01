# compilation_service/app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .sandbox import run_in_sandbox

app = FastAPI()

class CompilationRequest(BaseModel):
    source_code: str

@app.post("/compile")
async def compile_code(request: CompilationRequest):
    """
    Receives a compilation request and executes it in the sandbox.
    """
    # --- ADD THESE LINES FOR DEBUGGING ---
    print("\n--- COMPILATION SERVICE ---")
    print("Received code to compile:")
    print(request.source_code)
    print("---------------------------\n")
    # -------------------------------------

    if not request.source_code.strip():
        raise HTTPException(status_code=400, detail="source_code cannot be empty.")
    
    return await run_in_sandbox(request.source_code)