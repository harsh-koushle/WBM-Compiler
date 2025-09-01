from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID, uuid4
import httpx
from datetime import datetime
import os
from .models import (
    JobSubmissionRequest,
    JobSubmissionResponse,
    JobStatusResponse,
    JobOutputResponse,
)

app = FastAPI()

# --- CORS Middleware ---
# Allows your frontend to talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# --- Job Management ---
jobs = {}
COMPILATION_SERVICE_URL = os.getenv("COMPILATION_SERVICE_URL")

async def run_compilation(job_id: UUID, source_code: str):
    jobs[job_id]["status"] = "running"
    try:
        # --- THE FIX: Increased timeout for cold starts ---
        async with httpx.AsyncClient(timeout=45.0) as client:
            if not COMPILATION_SERVICE_URL:
                raise ValueError("COMPILATION_SERVICE_URL is not set.")
            
            response = await client.post(
                COMPILATION_SERVICE_URL,
                json={"source_code": source_code}
            )
            response.raise_for_status()
            result = response.json()
            jobs[job_id]["result"] = result
            jobs[job_id]["status"] = "completed"

    except httpx.RequestError as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["result"] = {
            "stdout": "",
            "stderr": f"Could not connect to the compilation service. It might be starting up. Please try again in a moment. Error: {e}",
            "exit_code": -1,
        }
    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["result"] = {
            "stdout": "",
            "stderr": f"An unexpected error occurred: {e}",
            "exit_code": -1,
        }

# --- API Endpoints ---
@app.post("/jobs", response_model=JobSubmissionResponse, status_code=202)
async def submit_job(
    request: JobSubmissionRequest, background_tasks: BackgroundTasks
):
    job_id = uuid4()
    jobs[job_id] = {"status": "pending", "created_at": datetime.utcnow()}
    background_tasks.add_task(run_compilation, job_id, request.source_code)
    return {"job_id": job_id}

@app.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: UUID):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    status_info = jobs[job_id].copy()
    status_info.pop("result", None)
    return {"job_id": job_id, **status_info}

@app.get("/jobs/{job_id}/output", response_model=JobOutputResponse)
async def get_job_output(job_id: UUID):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") not in ["completed", "error"]:
        raise HTTPException(status_code=400, detail="Job has not completed yet.")
    if "result" not in job:
        raise HTTPException(status_code=404, detail="Job result not found.")
    return job["result"]

# --- Frontend Serving ---
# This must be the last part of the file
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # This serves your index.html for any path that is not an API endpoint
    # This is useful for single-page applications with routing
    # Check if the path is trying to access a file in the frontend directory
    # This prevents directory traversal attacks
    file_path = os.path.join("frontend", full_path)
    if os.path.commonprefix((os.path.realpath(file_path), os.path.realpath("frontend"))) != os.path.realpath("frontend"):
        return FileResponse(os.path.join("frontend", "index.html"))

    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # For any other path, serve index.html
    return FileResponse(os.path.join("frontend", "index.html"))
