"""
app/routers/analysis.py
-----------------------
API endpoints for uploading and analyzing RFP documents.
"""

import os
import uuid
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks, Response, Cookie
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import structlog

from app.session_store import create_session, get_session, save_session
from app.services.pipeline_service import run_pipeline
from core.schemas import AnalysisState

log = structlog.get_logger(__name__)

router = APIRouter(tags=["analysis"])


class AnalysisResponse(BaseModel):
    session_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    status: str  # running | completed | failed
    progress: int  # 0-100
    current_step: str
    requirements_count: Optional[int] = None
    error: Optional[str] = None


# In-memory job tracking
_jobs = {}


async def run_analysis_background(
    session_id: str,
    file_path: str,
    title: str,
    min_confidence: float = 0.0
):
    """Background task to run the analysis pipeline."""
    try:
        _jobs[session_id] = {
            "status": "running",
            "progress": 10,
            "current_step": "Starting analysis...",
            "error": None
        }
        
        # Run pipeline
        final_state = await run_pipeline(
            file_path=file_path,
            title=title,
            min_confidence=min_confidence
        )
        
        # Update session with results
        ctx = get_session(session_id)
        if ctx:
            ctx.state = final_state
            save_session(session_id, ctx)
        
        _jobs[session_id] = {
            "status": "completed",
            "progress": 100,
            "current_step": "Analysis complete",
            "requirements_count": len(final_state.final_requirements),
            "error": None
        }
        
        log.info("analysis_complete", session_id=session_id, 
                requirements=len(final_state.final_requirements))
        
    except Exception as e:
        log.error("analysis_failed", session_id=session_id, error=str(e))
        _jobs[session_id] = {
            "status": "failed",
            "progress": 0,
            "current_step": "Failed",
            "error": str(e)
        }


@router.post("/api/analyze")
async def analyze_rfp(
    background_tasks: BackgroundTasks,
    response: Response,
    file: UploadFile = File(...),
    title: str = Form("RFP Analysis"),
    domain: Optional[str] = Form(None),
    min_confidence: float = Form(0.0)
):
    """Upload and analyze an RFP document."""
    
    # Validate file type
    allowed_extensions = {'.pdf', '.docx', '.txt'}
    file_ext = Path(file.filename or "file").suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(400, f"Unsupported file type: {file_ext}")
    
    # Save uploaded file
    upload_dir = Path("uploads") / str(uuid.uuid4())
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = upload_dir / (file.filename or "uploaded_file")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Create session
    session_id = create_session(str(file_path), title, domain)
    
    # Set session cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        max_age=14400,  # 4 hours
        samesite="lax"
    )
    
    # Start background analysis
    background_tasks.add_task(
        run_analysis_background,
        session_id,
        str(file_path),
        title,
        min_confidence
    )
    
    _jobs[session_id] = {
        "status": "pending",
        "progress": 0,
        "current_step": "Queued",
        "error": None
    }
    
    log.info("analysis_started", session_id=session_id, filename=file.filename)
    
    return AnalysisResponse(
        session_id=session_id,
        status="pending",
        message="Analysis started"
    )


@router.get("/api/status/{session_id}")
async def get_status(session_id: str):
    """Get analysis job status."""
    job = _jobs.get(session_id)
    if not job:
        raise HTTPException(404, "Job not found")
    
    return StatusResponse(**job)