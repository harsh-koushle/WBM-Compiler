from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from uuid import UUID, uuid4
import httpx
from datetime import datetime
import os
from .models import JobSubmissionRequest, JobSubmissionResponse, JobStatusResponse, JobOutputResponse

app = FastAPI()

# --- Configuration ---
jobs = {}
# For Render deployment, the URL will be set via an environment variable.
# For local development, we use the default.
COMPILATION_SERVICE_URL = os.getenv("COMPILATION_SERVICE_URL", "http://localhost:8001/compile")


# --- API Logic (This part is the same as before) ---
async def run_compilation(job_id: UUID, source_code: str):
    jobs[job_id]["status"] = "running"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(COMPILATION_SERVICE_URL, json={"source_code": source_code})
            response.raise_for_status()
            jobs[job_id]["result"] = response.json()
            jobs[job_id]["status"] = "completed"
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["result"] = {
            "stdout": "",
            "stderr": f"Error connecting to compilation service: {e}",
            "exit_code": -1,
        }

@app.post("/jobs", response_model=JobSubmissionResponse, status_code=202)
async def submit_job(request: JobSubmissionRequest, background_tasks: BackgroundTasks):
    job_id = uuid4()
    jobs[job_id] = {"status": "pending", "created_at": datetime.utcnow()}
    background_tasks.add_task(run_compilation, job_id, request.source_code)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}/output", response_model=JobOutputResponse)
async def get_job_output(job_id: UUID):
    job = jobs.get(job_id)
    if not job or "result" not in job:
        raise HTTPException(status_code=404, detail="Job result not found or not ready.")
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job has not completed yet.")
    return job["result"]


# --- NEW: Serve the Frontend ---

# Mount the 'frontend' directory to serve files like style.css and script.js
# This line MUST come before the root path route.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
async def read_index():
    # This route serves your main index.html file
    return FileResponse('frontend/index.html')
