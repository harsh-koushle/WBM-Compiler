from pydantic import BaseModel
from typing import Literal
from uuid import UUID, uuid4
from datetime import datetime

# Model for the incoming request body when creating a job
class JobSubmissionRequest(BaseModel):
    source_code: str

# Model for the response after submitting a job
class JobSubmissionResponse(BaseModel):
    job_id: UUID

# Model for checking the status of a job
class JobStatusResponse(BaseModel):
    job_id: UUID
    status: Literal['pending', 'running', 'completed', 'error']
    created_at: datetime

# Model for the final output of a completed job
class JobOutputResponse(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
