"""
web_app.py
----------
FastAPI web interface for RFP Analyzer.

Provides a browser-based UI for uploading RFP documents and viewing analysis results.
Now supports multi-file upload with optional Phase 0 document-consolidation pipeline.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
from datetime import datetime

import structlog
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import RFP analyzer components
from core.ingestor import ingest_document
from core.schemas import AnalysisState, Requirement, Category, Priority, ReviewStatus
from agents.functional import extract_functional
from agents.nonfunctional import extract_nonfunctional
from agents.compliance import extract_compliance
from agents.ambiguity import extract_ambiguities
from agents.risk import extract_risks
from agents.synthesizer import synthesize
from outputs.exporter import export_markdown, export_excel, export_json
from outputs.html_exporter import export_html
from outputs.html_exporter_by_module import export_html_by_module
from org_context import initialize_context_manager

# Phase 0 integration — optional; gracefully disabled when package is absent
from core.phase0_adapter import is_phase0_available, run_phase0, adapt_to_analyzer_chunks

PHASE0_AVAILABLE = is_phase0_available()

log = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RFP Analyzer",
    description="AI-powered RFP analysis with multi-agent system",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for analysis jobs
analysis_jobs: Dict[str, Dict[str, Any]] = {}


@app.on_event("startup")
async def _warmup():
    """
    Pre-load FAISS + SentenceTransformer at server startup so the first
    real /api/analyze request is never slow due to a cold model load.
    Runs in a thread pool to avoid blocking the event loop.
    """
    import asyncio
    import concurrent.futures

    def _load():
        try:
            from core.embedder import DocumentIndex
            from core.schemas import DocumentChunk
            # Build a tiny dummy index — enough to force model download/cache
            dummy = [DocumentChunk(section="warmup", text="warmup", page=1, char_count=6)]
            DocumentIndex(dummy)
            print("[STARTUP] Embedder pre-warmed (FAISS + SentenceTransformer ready)")
        except Exception as e:
            print(f"[STARTUP] Embedder warmup skipped: {e}")

    loop = asyncio.get_event_loop()
    loop.run_in_executor(concurrent.futures.ThreadPoolExecutor(max_workers=1), _load)


class AnalysisRequest(BaseModel):
    """Request model for analysis."""
    title: str = "RFP Analysis"
    org_context_url: Optional[str] = None
    min_confidence: float = 0.0


class AnalysisStatus(BaseModel):
    """Status model for analysis job."""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    current_step: str
    result_url: Optional[str] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


def _safe_title(title: str) -> str:
    return "".join(ch if ch.isalnum() or ch in (" ", "-", "_") else "_" for ch in title).strip() or "RFP_Analysis"


def _job_output_paths(job_id: str, title: str) -> dict[str, Path]:
    output_dir = Path("outputs") / "web" / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_title = _safe_title(title)
    base_name = safe_title.replace(' ', '_')
    return {
        "output_dir": output_dir,
        "markdown_path": output_dir / f"{base_name}.md",
        "excel_path": output_dir / f"{base_name}.xlsx",
        "json_path": output_dir / f"{base_name}.json",
        "html_category_path": output_dir / f"{base_name}_by_category.html",
        "html_module_path": output_dir / f"{base_name}_by_module.html",
    }


def _persist_job_exports(job_id: str) -> None:
    job = analysis_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    requirements = job.get("requirements_state")
    if requirements is None:
        raise HTTPException(status_code=400, detail="No requirements available")

    title = job.get("title", "RFP Analysis")
    paths = _job_output_paths(job_id, title)

    typed_requirements = [Requirement.model_validate(req) for req in requirements]

    export_markdown(typed_requirements, str(paths["markdown_path"]), rfp_title=title)
    export_excel(typed_requirements, str(paths["excel_path"]))
    export_json(typed_requirements, str(paths["json_path"]), rfp_title=title)
    export_html(typed_requirements, str(paths["html_category_path"]), rfp_title=title)
    export_html_by_module(typed_requirements, str(paths["html_module_path"]), rfp_title=title)

    job["markdown_path"] = str(paths["markdown_path"])
    job["excel_path"] = str(paths["excel_path"])
    job["json_path"] = str(paths["json_path"])
    job["html_category_path"] = str(paths["html_category_path"])
    job["html_module_path"] = str(paths["html_module_path"])


async def run_analysis(
    job_id: str,
    file_paths: List[Path],
    title: str,
    org_context_url: Optional[str] = None,
    min_confidence: float = 0.0,
    is_sap_opp: bool = False
):
    """
    Run RFP analysis in background.

    Supports single and multi-file uploads.  When multiple files are provided
    and Phase 0 is available, the Phase 0 document-consolidation pipeline runs
    first (classification → chunking → conflict detection → context assembly)
    before handing off to the standard agent pipeline.

    Args:
        job_id: Unique job identifier
        file_paths: List of uploaded RFP file paths
        title: Analysis title
        org_context_url: Optional organizational context URL
        min_confidence: Minimum confidence threshold
        is_sap_opp: Whether this is an SAP opportunity (enables SAP module mapping)
    """
    try:
        print(f"[ANALYSIS] Job {job_id} started for '{title}' ({len(file_paths)} file(s))")
        # Update status
        analysis_jobs[job_id]["status"] = "processing"
        analysis_jobs[job_id]["current_step"] = "Loading organizational context"
        analysis_jobs[job_id]["progress"] = 5
        analysis_jobs[job_id]["status_detail"] = "Initializing analysis pipeline"

        # Load organizational context if provided
        if org_context_url:
            try:
                print(f"[ANALYSIS] Loading organizational context for job {job_id}")
                analysis_jobs[job_id]["status_detail"] = "Loading organizational context"
                initialize_context_manager(org_context_url)
                log.info("org_context_loaded", url=org_context_url)
            except Exception as e:
                log.warning("org_context_load_failed", error=str(e))

        state = AnalysisState(file_path=str(file_paths[0]))
        state.metadata.update({
            "title": title,
            "min_confidence": min_confidence,
            "file_count": len(file_paths),
            "file_names": [fp.name for fp in file_paths],
        })

        # ── Step 1: Document ingestion ─────────────────────────────────────
        use_phase0 = PHASE0_AVAILABLE and len(file_paths) > 1

        if use_phase0:
            # ── Phase 0 path: multi-document consolidation ────────────────
            print(f"[ANALYSIS] Job {job_id}: running Phase 0 pipeline on {len(file_paths)} documents")
            analysis_jobs[job_id]["current_step"] = "Phase 0: Classifying & consolidating documents"
            analysis_jobs[job_id]["progress"] = 8
            analysis_jobs[job_id]["status_detail"] = (
                f"Running Phase 0 pipeline on {len(file_paths)} documents "
                "(classification → chunking → conflict detection → assembly)"
            )

            doc_context = run_phase0([str(fp) for fp in file_paths])

            if doc_context is not None:
                analysis_jobs[job_id]["status_detail"] = (
                    f"Phase 0 complete — "
                    f"{len(doc_context.documents)} docs, "
                    f"{len(doc_context.conflicts)} conflict(s) detected"
                )
                print(
                    f"[ANALYSIS] Job {job_id}: Phase 0 complete — "
                    f"{len(doc_context.documents)} docs, "
                    f"{len(doc_context.conflicts)} conflict(s)"
                )

                analyzer_chunks, phase0_meta = adapt_to_analyzer_chunks(doc_context, "phase1")
                state.chunks = analyzer_chunks
                state.document_text = "\n\n".join(c.text for c in analyzer_chunks)
                state.metadata.update({"phase0": phase0_meta})
                analysis_jobs[job_id]["phase0_meta"] = phase0_meta
                log.info("phase0_ingestion_done", chunks=len(state.chunks))
            else:
                # Phase 0 failed — fall back to standard ingestion
                print(f"[ANALYSIS] Job {job_id}: Phase 0 failed, falling back to standard ingestion")
                use_phase0 = False

        if not use_phase0:
            # ── Standard path: ingest each file with the existing ingestor ──
            print(f"[ANALYSIS] Job {job_id}: ingesting {len(file_paths)} document(s) via standard ingestor")
            analysis_jobs[job_id]["current_step"] = "Ingesting document(s)"
            analysis_jobs[job_id]["progress"] = 10
            analysis_jobs[job_id]["status_detail"] = (
                f"Parsing {len(file_paths)} uploaded document(s) into analysis chunks"
            )

            all_chunks = []
            for fp in file_paths:
                chunks = ingest_document(str(fp))
                all_chunks.extend(chunks)

            state.chunks = all_chunks
            state.document_text = "\n\n".join(c.text for c in state.chunks)

        analysis_jobs[job_id]["status_detail"] = (
            f"Document(s) parsed into {len(state.chunks)} chunks"
        )
        print(f"[ANALYSIS] Job {job_id}: ingestion complete — {len(state.chunks)} chunks")
        log.info("document_ingested", chunks=len(state.chunks))
        
        # Step 2: Extract functional requirements
        print(f"[ANALYSIS] Job {job_id}: extracting functional requirements")
        analysis_jobs[job_id]["current_step"] = "Extracting functional requirements"
        analysis_jobs[job_id]["progress"] = 25
        analysis_jobs[job_id]["status_detail"] = f"Running functional extraction across {len(state.chunks)} chunks"
        
        state.functional = extract_functional(state.chunks)
        if min_confidence > 0.0:
            state.functional = [
                req for req in state.functional if req.confidence >= min_confidence
            ]
        analysis_jobs[job_id]["status_detail"] = f"Functional extraction complete: {len(state.functional)} requirements found"
        print(f"[ANALYSIS] Job {job_id}: functional extraction complete ({len(state.functional)} requirements)")
        log.info("functional_extracted", count=len(state.functional))
        
        # Step 3: Extract non-functional requirements
        print(f"[ANALYSIS] Job {job_id}: extracting non-functional requirements")
        analysis_jobs[job_id]["current_step"] = "Extracting non-functional requirements"
        analysis_jobs[job_id]["progress"] = 40
        analysis_jobs[job_id]["status_detail"] = f"Running non-functional extraction across {len(state.chunks)} chunks"
        
        state.non_functional = extract_nonfunctional(state.chunks)
        if min_confidence > 0.0:
            state.non_functional = [
                req for req in state.non_functional if req.confidence >= min_confidence
            ]
        analysis_jobs[job_id]["status_detail"] = f"Non-functional extraction complete: {len(state.non_functional)} requirements found"
        print(f"[ANALYSIS] Job {job_id}: non-functional extraction complete ({len(state.non_functional)} requirements)")
        log.info("nonfunctional_extracted", count=len(state.non_functional))
        
        # Step 4: Extract compliance requirements
        print(f"[ANALYSIS] Job {job_id}: extracting compliance requirements")
        analysis_jobs[job_id]["current_step"] = "Extracting compliance requirements"
        analysis_jobs[job_id]["progress"] = 55
        analysis_jobs[job_id]["status_detail"] = f"Running compliance extraction across {len(state.chunks)} chunks"
        
        state.compliance = extract_compliance(state.chunks)
        if min_confidence > 0.0:
            state.compliance = [
                req for req in state.compliance if req.confidence >= min_confidence
            ]
        analysis_jobs[job_id]["status_detail"] = f"Compliance extraction complete: {len(state.compliance)} requirements found"
        print(f"[ANALYSIS] Job {job_id}: compliance extraction complete ({len(state.compliance)} requirements)")
        log.info("compliance_extracted", count=len(state.compliance))
        
        # Step 5: Detect ambiguities
        print(f"[ANALYSIS] Job {job_id}: detecting ambiguities")
        analysis_jobs[job_id]["current_step"] = "Detecting ambiguities"
        analysis_jobs[job_id]["progress"] = 70
        analysis_jobs[job_id]["status_detail"] = f"Running ambiguity detection across {len(state.chunks)} chunks"
        
        state.ambiguities = extract_ambiguities(state.chunks)
        if min_confidence > 0.0:
            state.ambiguities = [
                req for req in state.ambiguities if req.confidence >= min_confidence
            ]
        analysis_jobs[job_id]["status_detail"] = f"Ambiguity detection complete: {len(state.ambiguities)} items found"
        print(f"[ANALYSIS] Job {job_id}: ambiguity detection complete ({len(state.ambiguities)} items)")
        log.info("ambiguities_detected", count=len(state.ambiguities))
        
        # Step 6: Assess risks
        print(f"[ANALYSIS] Job {job_id}: assessing risks")
        analysis_jobs[job_id]["current_step"] = "Assessing risks"
        analysis_jobs[job_id]["progress"] = 85
        analysis_jobs[job_id]["status_detail"] = f"Running risk assessment across {len(state.chunks)} chunks"
        
        state.risks = extract_risks(state.chunks)
        if min_confidence > 0.0:
            state.risks = [
                req for req in state.risks if req.confidence >= min_confidence
            ]
        analysis_jobs[job_id]["status_detail"] = f"Risk assessment complete: {len(state.risks)} items found"
        print(f"[ANALYSIS] Job {job_id}: risk assessment complete ({len(state.risks)} items)")
        log.info("risks_assessed", count=len(state.risks))
        
        # Step 7: Synthesize results
        print(f"[ANALYSIS] Job {job_id}: synthesizing results")
        analysis_jobs[job_id]["current_step"] = "Synthesizing results"
        analysis_jobs[job_id]["progress"] = 95
        analysis_jobs[job_id]["status_detail"] = "Deduplicating and organizing extracted requirements"
        
        state.final_requirements = synthesize(state.all_raw_requirements())
        
        # Step 7.5: SAP Module Mapping (if SAP opportunity)
        if is_sap_opp:
            analysis_jobs[job_id]["current_step"] = "Mapping to SAP modules"
            analysis_jobs[job_id]["progress"] = 97
            
            try:
                from agents.sap_mapping_agent import map_to_sap_modules
                state.final_requirements = map_to_sap_modules(state.final_requirements)
                log.info("sap_mapping_completed", count=len(state.final_requirements))
            except Exception as e:
                log.warning("sap_mapping_failed", error=str(e))
        
        # Step 8: Prepare editable review state
        print(f"[ANALYSIS] Job {job_id}: preparing review workspace")
        analysis_jobs[job_id]["current_step"] = "Preparing review workspace"
        analysis_jobs[job_id]["progress"] = 98
        analysis_jobs[job_id]["status_detail"] = f"Preparing {len(state.final_requirements)} requirements for review and export"
        
        analysis_jobs[job_id]["requirements_state"] = [
            req.model_dump(mode="json") for req in state.final_requirements
        ]
        analysis_jobs[job_id]["has_unsaved_changes"] = False
        _persist_job_exports(job_id)
        
        # Update status to completed
        analysis_jobs[job_id]["status"] = "completed"
        analysis_jobs[job_id]["progress"] = 100
        analysis_jobs[job_id]["current_step"] = "Analysis complete"
        analysis_jobs[job_id]["status_detail"] = f"Completed with {len(state.final_requirements)} reviewed requirements ready"
        analysis_jobs[job_id]["result_url"] = f"/api/results/{job_id}"
        analysis_jobs[job_id]["completed_at"] = datetime.now()
        
        log.info("analysis_completed", job_id=job_id)
        
    except Exception as e:
        print(f"[ANALYSIS] Job {job_id} failed: {e}")
        log.error("analysis_failed", job_id=job_id, error=str(e))
        analysis_jobs[job_id]["status"] = "failed"
        analysis_jobs[job_id]["status_detail"] = "Analysis failed before completion"
        analysis_jobs[job_id]["error"] = str(e)
        analysis_jobs[job_id]["completed_at"] = datetime.now()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface."""
    html_path = Path(__file__).parent / "web" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    
    # Return inline HTML if file doesn't exist
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RFP Analyzer</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #f5f5f5;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }
            
            /* Top Header Band with Upload Section */
            .top-header {
                background: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 16px 24px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }

            .top-header-inner {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 24px;
                width: 100%;
            }
            
            .logo-section {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .logo-icon {
                font-size: 1.8em;
            }
            
            .logo-text {
                font-size: 1.25em;
                font-weight: 700;
                color: #667eea;
            }
            
            .upload-section {
                display: flex;
                align-items: center;
                gap: 12px;
                flex-wrap: wrap;
                justify-content: flex-end;
                margin-left: auto;
            }
            
            .upload-label {
                font-size: 0.875em;
                color: #666;
                font-weight: 500;
            }
            
            .file-input-wrapper {
                position: relative;
                display: inline-block;
            }
            
            .file-input-btn {
                padding: 8px 16px;
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.875em;
                color: #333;
                transition: all 0.2s;
            }
            
            .file-input-btn:hover {
                border-color: #667eea;
                background: #f8f9ff;
            }
            
            .domain-input {
                padding: 8px 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 0.875em;
                width: 120px;
            }
            
            .confidence-input {
                padding: 8px 12px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 0.875em;
                width: 80px;
            }
            
            .analyze-btn {
                padding: 8px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.875em;
                font-weight: 600;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            
            .analyze-btn:hover {
                background: #5568d3;
            }
            
            .analyze-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .home-btn {
                padding: 8px 16px;
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                cursor: pointer;
                font-size: 0.875em;
                color: #333;
                text-decoration: none;
                display: flex;
                align-items: center;
                gap: 6px;
                transition: all 0.2s;
            }
            
            .home-btn:hover {
                border-color: #667eea;
                background: #f8f9ff;
            }
            
            /* Tab Navigation */
            .tab-navigation {
                background: white;
                border-bottom: 1px solid #e0e0e0;
                padding: 0 24px;
            }

            .tab-navigation-inner {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                gap: 0;
                width: 100%;
            }
            
            .tab-btn {
                padding: 14px 24px;
                background: none;
                border: none;
                border-bottom: 2px solid transparent;
                cursor: pointer;
                font-size: 0.875em;
                font-weight: 600;
                color: #666;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .tab-btn:hover {
                color: #333;
                background: #f8f9ff;
            }
            
            .tab-btn.active {
                color: #667eea;
                border-bottom-color: #667eea;
            }
            
            /* Main Content Area */
            .main-content {
                flex: 1;
                padding: 24px;
                overflow-y: auto;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }
            
            .page-title {
                font-size: 1.5em;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 20px;
            }
            /* Filter Section */
            .filter-section {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 24px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
            }
            
            .filter-group {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }
            
            .filter-label {
                font-size: 0.75em;
                font-weight: 600;
                color: #555;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .filter-select {
                padding: 10px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 0.875em;
                background: white;
                cursor: pointer;
            }
            
            .filter-input {
                padding: 10px;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-size: 0.875em;
            }
            
            /* Action Buttons */
            .action-buttons {
                display: flex;
                gap: 12px;
                margin-bottom: 24px;
            }
            
            .action-btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                font-size: 0.875em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .btn-accept {
                background: #10b981;
                color: white;
            }
            
            .btn-accept:hover {
                background: #059669;
            }
            
            .btn-reject {
                background: #ef4444;
                color: white;
            }
            
            .btn-reject:hover {
                background: #dc2626;
            }
            
            input[type="file"] {
                display: none;
            }
            
            input[type="text"]:focus, input[type="number"]:focus, .filter-select:focus, .filter-input:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .file-name-badge {
                display: inline-block;
                padding: 4px 12px;
                background: #DCFCE7;
                color: #15803D;
                border-radius: 12px;
                font-size: 0.75em;
                font-weight: 600;
                margin-left: 8px;
            }
            .progress-container {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #F0FDF4;
                border-radius: 8px;
                border-left: 4px solid #10B981;
            }
            .progress-bar {
                width: 100%;
                height: 32px;
                background: #E5E7EB;
                border-radius: 16px;
                overflow: hidden;
                margin-bottom: 12px;
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 600;
                font-size: 13px;
                border-radius: 16px;
            }
            .progress-text {
                text-align: center;
                color: #065F46;
                margin-bottom: 8px;
                font-weight: 600;
                font-size: 14px;
            }
            .results {
                display: none;
                margin-top: 20px;
                padding: 20px;
                background: #F0FDF4;
                border-radius: 8px;
                border-left: 4px solid #10B981;
            }
            .results h2 {
                color: #059669;
                margin-bottom: 12px;
                font-size: 18px;
                font-weight: 600;
            }
            .results p {
                color: #065F46;
                font-size: 14px;
                line-height: 1.5;
            }
            .download-btn {
                display: inline-block;
                margin: 10px 10px 0 0;
                padding: 10px 20px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }
            .download-btn:hover {
                background: #764ba2;
            }
            .error {
                display: none;
                margin-top: 20px;
                padding: 15px;
                background: #fee;
                border: 2px solid #fcc;
                border-radius: 8px;
                color: #c33;
            }
            
            /* Layout Grid */
            .main-grid {
                display: grid;
                grid-template-columns: 500px 1fr;
                gap: 30px;
                max-width: 1600px;
                margin: 0 auto;
            }
            
            @media (max-width: 1200px) {
                .main-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            /* HTML Output Viewer - Integrated in Grid */
            .html-output-viewer {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                min-height: 600px;
                display: none;
            }
            .html-output-viewer.show {
                display: block;
            }
            .html-output-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 20px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                user-select: none;
            }
            .html-output-header:hover {
                opacity: 0.9;
            }
            .html-output-title {
                font-weight: 600;
                font-size: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .toggle-icon {
                font-size: 24px;
                transition: transform 0.3s ease;
            }
            .html-output-viewer.collapsed .toggle-icon {
                transform: rotate(180deg);
            }
            .html-output-content {
                padding: 20px;
                overflow-y: auto;
                max-height: calc(60vh - 50px);
                background: #f8f9fa;
            }
            .html-output-viewer.collapsed .html-output-content {
                display: none;
            }
            .html-output-iframe {
                width: 100%;
                min-height: 500px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
            .no-output-message {
                text-align: center;
                color: #999;
                padding: 60px 20px;
                font-size: 1.1em;
            }
            .view-selector {
                display: flex;
                gap: 10px;
                margin-bottom: 15px;
            }
            .view-btn {
                padding: 8px 16px;
                border: 2px solid #667eea;
                background: white;
                color: #667eea;
                border-radius: 5px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s;
            }
            .view-btn.active {
                background: #667eea;
                color: white;
            }
            .view-btn:hover {
                background: #667eea;
                color: white;
            }
        </style>
    </head>
    <body>
        <!-- Top Header Band with Upload Section -->
        <div class="top-header">
            <div class="top-header-inner">
                <div class="logo-section">
                    <span class="logo-icon">🤖</span>
                    <span class="logo-text">RFP Analyzer</span>
                </div>
                
                <form id="uploadForm" class="upload-section">
                    <span class="upload-label">📄 Upload RFP</span>
                    <div class="file-input-wrapper">
                        <label for="fileInput" class="file-input-btn">
                            Choose File(s)
                        </label>
                        <input type="file" id="fileInput" accept=".pdf,.docx,.txt" multiple required>
                        <span id="fileName" class="file-name-badge" style="display: none;"></span>
                    </div>
                    
                    <input type="text" id="domainInput" class="domain-input" placeholder="Domain (optional)" title="Domain/Industry (optional)">
                    <input type="number" id="minConfidence" class="confidence-input" value="0.0" min="0" max="1" step="0.1" title="Minimum Confidence (0.0 - 1.0)">
                    <input type="hidden" id="title" value="RFP Analysis">
                    <input type="hidden" id="orgContext" value="">
                    <input type="hidden" id="isSapOpp" value="false">
                    
                    <button type="submit" id="analyzeBtn" class="analyze-btn">
                        🔍 Analyze
                    </button>
                </form>
                
                <a href="/" class="home-btn">
                    🏠 Home
                </a>
            </div>
        </div>
        
        <!-- Tab Navigation -->
        <div class="tab-navigation">
            <div class="tab-navigation-inner">
                <button class="tab-btn active" data-tab="requirements">
                    📋 Requirements
                </button>
                <button class="tab-btn" data-tab="architecture">
                    🏗️ Architecture
                </button>
                <button class="tab-btn" data-tab="solution">
                    🔧 Solution Mapping
                </button>
                <button class="tab-btn" data-tab="export">
                    📤 Export
                </button>
            </div>
        </div>
        
        <!-- Main Content Area -->
        <div class="main-content">
            <div class="container">
                <!-- Requirements Tab Content -->
                <div id="requirements-tab" class="tab-content">
                    <h2 class="page-title">Review Requirements</h2>
                    
                    <!-- Filter Section -->
                    <div class="filter-section">
                        <div class="filter-group">
                            <label class="filter-label">Category</label>
                            <select class="filter-select" id="categoryFilter">
                                <option value="all">All Categories</option>
                                <option value="functional">Functional</option>
                                <option value="non_functional">Non-Functional</option>
                                <option value="compliance">Compliance</option>
                                <option value="ambiguity">Ambiguity</option>
                                <option value="risk">Risk</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Priority</label>
                            <select class="filter-select" id="priorityFilter">
                                <option value="all">All Priorities</option>
                                <option value="must">Must</option>
                                <option value="should">Should</option>
                                <option value="could">Could</option>
                                <option value="wont">Won't</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Review Status</label>
                            <select class="filter-select" id="statusFilter">
                                <option value="all">All Statuses</option>
                                <option value="pending">Pending</option>
                                <option value="accepted">Accepted</option>
                                <option value="modified">Modified</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                        
                        <div class="filter-group">
                            <label class="filter-label">Search</label>
                            <input type="text" class="filter-input" id="searchInput" placeholder="Search...">
                        </div>

                        <div class="filter-group">
                            <label class="filter-label">Min Confidence</label>
                            <input type="range" class="filter-input" id="confidenceFilter" min="0" max="1" step="0.05" value="0">
                            <span id="confidenceValue" style="font-size: 0.8em; color: #666;">0.00</span>
                        </div>
                    </div>
                    
                    <!-- Action Buttons -->
                    <div class="action-buttons" style="justify-content: space-between; align-items: center; flex-wrap: wrap;">
                        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                            <button class="action-btn btn-accept" id="acceptVisibleBtn">✓ Accept Visible</button>
                            <button class="action-btn btn-reject" id="rejectVisibleBtn">✗ Reject Visible</button>
                            <button class="action-btn" id="resetFiltersBtn" style="background: #6B7280; color: white;">↺ Reset Filters</button>
                        </div>
                        <div style="font-size: 0.875em; color: #666;">
                            <span id="filterSummary">0 requirements shown</span>
                        </div>
                    </div>
                    
                    <!-- Progress Container -->
                    <div class="progress-container" id="progressContainer">
                        <div class="progress-text" id="progressText">Initializing...</div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill" style="width: 0%">0%</div>
                        </div>
                        <div class="progress-text" id="stepText"></div>
                        <div class="progress-text" id="statusDetailText" style="font-weight: 500; color: #374151;"></div>
                        <div class="progress-text" id="elapsedTimeText" style="font-weight: 500; color: #6B7280; font-size: 13px;"></div>
                    </div>
                    
                    <!-- Phase 0 Conflict Banner (shown only when conflicts exist) -->
                    <div id="phase0Banner" style="display:none; margin-bottom:16px; padding:14px 18px; background:#FFF7ED; border:1px solid #FED7AA; border-left:4px solid #F97316; border-radius:8px; font-size:0.875em; color:#7C2D12;">
                        <strong>⚠️ Phase 0: Cross-document conflicts detected</strong>
                        <div id="phase0BannerBody" style="margin-top:6px; line-height:1.6;"></div>
                    </div>

                    <!-- Results -->
                    <div class="results" id="results">
                        <h2>✅ Analysis Complete!</h2>
                        <p>Your RFP has been analyzed successfully. Review and edit requirements, click <strong>Save Changes</strong>, then use the <strong>Export</strong> tab when you are satisfied.</p>
                    </div>
                    
                    <!-- Error Display -->
                    <div class="error" id="error"></div>
                    
                    <!-- Requirements List -->
                    <div id="requirementsList" style="margin-top: 20px;">
                        <p id="requirementsEmptyState" style="text-align: center; color: #999; padding: 40px;">
                            Upload and analyze an RFP document to review extracted requirements here.
                        </p>
                    </div>
                </div>
                
                <!-- Architecture Tab Content -->
                <div id="architecture-tab" class="tab-content" style="display: none;">
                    <h2 class="page-title">Architecture</h2>
                    <p style="color: #666;">Architecture view will be displayed here after analysis.</p>
                </div>
                
                <!-- Solution Mapping Tab Content -->
                <div id="solution-tab" class="tab-content" style="display: none;">
                    <h2 class="page-title">Solution Mapping</h2>
                    <p style="color: #666;">Solution mapping will be displayed here after analysis.</p>
                </div>
                
                <!-- Export Tab Content -->
                <div id="export-tab" class="tab-content" style="display: none;">
                    <h2 class="page-title">Export</h2>
                    <div style="background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 10px; padding: 20px;">
                        <p id="exportStatusMessage" style="color: #666; margin-bottom: 16px;">
                            Complete an analysis, review the requirements, and save your changes before exporting.
                        </p>
                        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                            <a href="#" id="downloadMarkdown" class="download-btn" target="_blank" style="pointer-events: none; opacity: 0.5;">📄 Markdown</a>
                            <a href="#" id="downloadExcel" class="download-btn" target="_blank" style="pointer-events: none; opacity: 0.5;">📊 Excel</a>
                            <a href="#" id="downloadJson" class="download-btn" target="_blank" style="pointer-events: none; opacity: 0.5;">🔧 JSON</a>
                            <button id="showHtmlOutputBtn" class="download-btn" style="background: #27AE60; border: none; cursor: not-allowed; opacity: 0.5;" disabled>👁️ Show HTML Output</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
            
        <script>
            const fileInput = document.getElementById('fileInput');
            const fileName = document.getElementById('fileName');
            const uploadForm = document.getElementById('uploadForm');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const progressContainer = document.getElementById('progressContainer');
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            const stepText = document.getElementById('stepText');
            const statusDetailText = document.getElementById('statusDetailText');
            const elapsedTimeText = document.getElementById('elapsedTimeText');
            const results = document.getElementById('results');
            const errorDiv = document.getElementById('error');
            
            // HTML Viewer variables
            let currentJobId = null;
            let allRequirements = [];
            let filteredRequirements = [];
            let hasUnsavedChanges = false;
            let hasSavedRequirements = false;
            let analysisStartedAt = null;
            let currentPhase0Meta = null;

            function renderPhase0Banner(phase0Meta) {
                const banner = document.getElementById('phase0Banner');
                const body = document.getElementById('phase0BannerBody');
                if (!phase0Meta || !phase0Meta.phase0_conflict_count) {
                    banner.style.display = 'none';
                    return;
                }
                const conflicts = phase0Meta.phase0_conflicts || [];
                const docsNeedingReview = phase0Meta.phase0_docs_needing_review || [];
                let html = `<strong>${phase0Meta.phase0_conflict_count} conflict(s)</strong> found across ${(phase0Meta.phase0_docs || []).length} document(s).`;
                if (conflicts.length) {
                    html += '<ul style="margin:6px 0 0 16px;">';
                    conflicts.forEach(c => {
                        const sev = c.severity ? ` [${c.severity}]` : '';
                        html += `<li><strong>${c.conflict_id}${sev}</strong>: ${escapeHtml(c.description)} <em>(${(c.source_documents || []).join(', ')})</em></li>`;
                    });
                    html += '</ul>';
                }
                if (docsNeedingReview.length) {
                    html += `<div style="margin-top:6px;">Documents flagged for manual review: ${docsNeedingReview.map(d => `<code>${escapeHtml(d)}</code>`).join(', ')}</div>`;
                }
                body.innerHTML = html;
                banner.style.display = 'block';
            }
            
            // Tab Switching
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    // Remove active class from all tabs
                    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
                    
                    // Add active class to clicked tab
                    btn.classList.add('active');
                    const tabId = btn.getAttribute('data-tab') + '-tab';
                    document.getElementById(tabId).style.display = 'block';
                });
            });
            
            function escapeHtml(value) {
                return String(value ?? '')
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }


            function formatConfidence(value) {
                const num = Number(value ?? 0);
                return Number.isFinite(num) ? num.toFixed(2) : '0.00';
            }

            function updateFilterSummary() {
                const summary = document.getElementById('filterSummary');
                summary.textContent = `${filteredRequirements.length} of ${allRequirements.length} requirements shown`;
            }

            function setExportEnabled(enabled) {
                ['downloadMarkdown', 'downloadExcel', 'downloadJson'].forEach((id) => {
                    const element = document.getElementById(id);
                    element.style.pointerEvents = enabled ? 'auto' : 'none';
                    element.style.opacity = enabled ? '1' : '0.5';
                });

                const htmlBtn = document.getElementById('showHtmlOutputBtn');
                htmlBtn.disabled = !enabled;
                htmlBtn.style.cursor = enabled ? 'pointer' : 'not-allowed';
                htmlBtn.style.opacity = enabled ? '1' : '0.5';
            }

            function updateSaveState() {
                const saveBtn = document.getElementById('saveRequirementsBtn');
                const saveStatus = document.getElementById('saveStatus');
                const exportStatusMessage = document.getElementById('exportStatusMessage');

                if (!exportStatusMessage) {
                    return;
                }

                if (!saveBtn || !saveStatus) {
                    exportStatusMessage.textContent = 'Review the requirements table to enable saving, then export once changes are saved.';
                    exportStatusMessage.style.color = '#666';
                    setExportEnabled(false);
                    return;
                }

                if (!currentJobId || allRequirements.length === 0) {
                    saveBtn.disabled = true;
                    saveBtn.textContent = '💾 Save Changes';
                    saveStatus.textContent = 'No analysis loaded';
                    saveStatus.style.color = '#6B7280';
                    exportStatusMessage.textContent = 'Complete an analysis, review the requirements, and save your changes before exporting.';
                    exportStatusMessage.style.color = '#666';
                    setExportEnabled(false);
                    return;
                }

                if (hasUnsavedChanges) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = '💾 Save Changes';
                    saveStatus.textContent = 'Unsaved changes';
                    saveStatus.style.color = '#B45309';
                    exportStatusMessage.textContent = 'You have unsaved edits. Save changes before exporting updated requirements.';
                    exportStatusMessage.style.color = '#B45309';
                    setExportEnabled(false);
                    return;
                }

                if (hasSavedRequirements) {
                    saveBtn.disabled = true;
                    saveBtn.textContent = '✅ Saved';
                    saveStatus.textContent = 'All changes saved';
                    saveStatus.style.color = '#059669';
                    exportStatusMessage.textContent = 'Exports will use your latest saved requirement edits.';
                    exportStatusMessage.style.color = '#059669';
                    setExportEnabled(true);
                    return;
                }

                saveBtn.disabled = true;
                saveBtn.textContent = '💾 Save Changes';
                saveStatus.textContent = 'No saved review state yet';
                saveStatus.style.color = '#6B7280';
                exportStatusMessage.textContent = 'Review the requirements and click Save Changes before exporting.';
                exportStatusMessage.style.color = '#666';
                setExportEnabled(false);
            }

            function markDirty() {
                hasUnsavedChanges = true;
                hasSavedRequirements = false;
                errorDiv.style.display = 'none';
                updateSaveState();
            }

            function getCurrentFilters() {
                return {
                    category: document.getElementById('categoryFilter').value,
                    priority: document.getElementById('priorityFilter').value,
                    status: document.getElementById('statusFilter').value,
                    search: document.getElementById('searchInput').value.trim().toLowerCase(),
                    minConfidence: Number(document.getElementById('confidenceFilter').value || 0)
                };
            }

            function applyFiltersAndRender() {
                const filters = getCurrentFilters();

                filteredRequirements = allRequirements.filter((req) => {
                    const matchesCategory = filters.category === 'all' || (req.category || '') === filters.category;
                    const matchesPriority = filters.priority === 'all' || (req.priority || '') === filters.priority;
                    const matchesStatus = filters.status === 'all' || (req.review_status || 'pending') === filters.status;
                    const matchesConfidence = Number(req.confidence || 0) >= filters.minConfidence;
                    const haystack = `${req.id || ''} ${req.title || ''} ${req.description || ''} ${req.source_section || ''}`.toLowerCase();
                    const matchesSearch = !filters.search || haystack.includes(filters.search);

                    return matchesCategory && matchesPriority && matchesStatus && matchesConfidence && matchesSearch;
                });

                renderRequirements(filteredRequirements);
                updateFilterSummary();
            }

            function updateRequirement(requirementId, field, value) {
                const req = allRequirements.find((item) => (item.id || '') === (requirementId || ''));
                if (!req) return;

                req[field] = value;

                if (field !== 'review_status' && req.review_status === 'pending') {
                    req.review_status = 'modified';
                }

                markDirty();
                applyFiltersAndRender();
            }

            function renderSelectEditor(requirementId, field, value, options) {
                return `
                    <select
                        onchange="updateRequirement('${escapeHtml(requirementId)}', '${field}', this.value)"
                        style="width: 100%; padding: 6px 8px; border: 1px solid #D1D5DB; border-radius: 6px; font-size: 0.85rem; background: white;"
                    >
                        ${options.map(option => `
                            <option value="${escapeHtml(option.value)}" ${option.value === value ? 'selected' : ''}>
                                ${escapeHtml(option.label)}
                            </option>
                        `).join('')}
                    </select>
                `;
            }

            function renderRequirements(requirements) {
                const container = document.getElementById('requirementsList');
                const emptyState = document.getElementById('requirementsEmptyState');

                if (!requirements || requirements.length === 0) {
                    container.innerHTML = `
                        <p style="text-align: center; color: #999; padding: 40px;">
                            No requirements matched the current filters.
                        </p>
                    `;
                    updateFilterSummary();
                    return;
                }

                if (emptyState) {
                    emptyState.remove();
                }

                const categoryOptions = [
                    { value: 'functional', label: 'Functional' },
                    { value: 'non_functional', label: 'Non-Functional' },
                    { value: 'compliance', label: 'Compliance' },
                    { value: 'ambiguity', label: 'Ambiguity' },
                    { value: 'risk', label: 'Risk' }
                ];

                const priorityOptions = [
                    { value: 'must', label: 'Must' },
                    { value: 'should', label: 'Should' },
                    { value: 'could', label: 'Could' },
                    { value: 'wont', label: 'Won’t' }
                ];

                const statusOptions = [
                    { value: 'pending', label: 'Pending' },
                    { value: 'accepted', label: 'Accepted' },
                    { value: 'modified', label: 'Modified' },
                    { value: 'rejected', label: 'Rejected' }
                ];

                const rows = requirements.map((req, index) => {
                    const requirementId = req.id || `REQ-${String(index + 1).padStart(3, '0')}`;
                    const title = req.title || `Requirement ${index + 1}`;
                    const description = req.description || '';
                    const category = req.category || 'functional';
                    const priority = req.priority || 'must';
                    const reviewStatus = req.review_status || 'pending';
                    const confidence = formatConfidence(req.confidence);
                    const sourceSection = req.source_section || '—';
                    const pageRef = req.page_ref || '—';
                    const notes = req.reviewer_notes || '';

                    return `
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">${escapeHtml(requirementId)}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">${renderSelectEditor(requirementId, 'category', category, categoryOptions)}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">
                                <div style="font-weight: 600; color: #111827; margin-bottom: 6px;">${escapeHtml(title)}</div>
                                <div style="color: #4B5563; line-height: 1.5;">${escapeHtml(description)}</div>
                                <div style="margin-top: 8px; font-size: 0.8rem; color: #6B7280;">
                                    <strong>Source:</strong> ${escapeHtml(sourceSection)} &nbsp;|&nbsp;
                                    <strong>Page:</strong> ${escapeHtml(pageRef)} &nbsp;|&nbsp;
                                    <strong>Ambiguous:</strong> ${req.ambiguity_flag ? 'Yes' : 'No'}
                                </div>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">${renderSelectEditor(requirementId, 'priority', priority, priorityOptions)}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">
                                <input
                                    type="number"
                                    min="0"
                                    max="1"
                                    step="0.05"
                                    value="${escapeHtml(confidence)}"
                                    onchange="updateRequirement('${escapeHtml(requirementId)}', 'confidence', Number(this.value))"
                                    style="width: 90px; padding: 6px 8px; border: 1px solid #D1D5DB; border-radius: 6px; font-size: 0.85rem;"
                                >
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">${renderSelectEditor(requirementId, 'review_status', reviewStatus, statusOptions)}</td>
                            <td style="padding: 10px; border-bottom: 1px solid #E5E7EB; vertical-align: top;">
                                <textarea
                                    onchange="updateRequirement('${escapeHtml(requirementId)}', 'reviewer_notes', this.value)"
                                    placeholder="Add reviewer notes..."
                                    style="width: 100%; min-width: 220px; min-height: 72px; padding: 8px 10px; border: 1px solid #D1D5DB; border-radius: 8px; font-size: 0.9rem; resize: vertical;"
                                >${escapeHtml(notes)}</textarea>
                            </td>
                        </tr>
                    `;
                }).join('');

                container.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 16px;">
                        <div id="saveStatus" style="font-size: 0.9rem; font-weight: 600; color: #6B7280;">No analysis loaded</div>
                        <button id="saveRequirementsBtn" type="button" class="action-btn" style="background: #2563EB; color: white;" disabled>💾 Save Changes</button>
                    </div>
                    <div style="overflow-x: auto; border: 1px solid #E5E7EB; border-radius: 10px; background: white;">
                        <table style="width: 100%; border-collapse: collapse; min-width: 1200px;">
                            <thead style="background: #F9FAFB;">
                                <tr>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">ID</th>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">Category</th>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">Requirement</th>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">Priority</th>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">Confidence</th>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">Review Status</th>
                                    <th style="text-align: left; padding: 12px 10px; border-bottom: 1px solid #E5E7EB; font-size: 0.78rem; text-transform: uppercase; color: #6B7280;">Reviewer Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${rows}
                            </tbody>
                        </table>
                    </div>
                `;

                const saveBtn = document.getElementById('saveRequirementsBtn');
                if (saveBtn) {
                    saveBtn.addEventListener('click', async () => {
                        try {
                            await saveRequirements(true);
                        } catch (error) {
                            errorDiv.textContent = 'Save failed: ' + error.message;
                            errorDiv.style.display = 'block';
                        }
                    });
                }

                updateFilterSummary();
            }

            async function saveRequirements(showSuccess = false) {
                if (!currentJobId) return;

                const saveBtn = document.getElementById('saveRequirementsBtn');
                saveBtn.disabled = true;
                saveBtn.textContent = '⏳ Saving...';

                const response = await fetch(`/api/requirements/${currentJobId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ requirements: allRequirements })
                });

                const data = await response.json();
                if (!response.ok) {
                    saveBtn.textContent = '💾 Save Changes';
                    throw new Error(data.detail || 'Failed to save requirement changes');
                }

                hasUnsavedChanges = false;
                hasSavedRequirements = true;
                updateSaveState();

                if (showSuccess) {
                    errorDiv.style.display = 'none';
                }

                return data;
            }

            async function bulkUpdateVisible(status) {
                filteredRequirements.forEach((req) => {
                    req.review_status = status;
                    const original = allRequirements.find((item) => (item.id || '') === (req.id || '') && item.title === req.title && item.description === req.description);
                    if (original) {
                        original.review_status = status;
                    }
                });

                markDirty();
                applyFiltersAndRender();
            }

            function resetFilters() {
                document.getElementById('categoryFilter').value = 'all';
                document.getElementById('priorityFilter').value = 'all';
                document.getElementById('statusFilter').value = 'all';
                document.getElementById('searchInput').value = '';
                document.getElementById('confidenceFilter').value = '0';
                document.getElementById('confidenceValue').textContent = '0.00';
                applyFiltersAndRender();
            }

            async function loadRequirements(jobId) {
                const container = document.getElementById('requirementsList');
                container.innerHTML = `
                    <p style="text-align: center; color: #6B7280; padding: 40px;">
                        Loading extracted requirements...
                    </p>
                `;

                try {
                    let requirements = [];

                    const response = await fetch(`/api/download/${jobId}/json`);
                    if (response.ok) {
                        const data = await response.json();
                        requirements = Array.isArray(data?.requirements)
                            ? data.requirements
                            : Array.isArray(data)
                                ? data
                                : [];
                    } else {
                        const statusResponse = await fetch(`/api/status/${jobId}`);
                        const statusData = await statusResponse.json();
                        requirements = Array.isArray(statusData?.requirements_state)
                            ? statusData.requirements_state
                            : [];
                    }

                    allRequirements = requirements.map((req, index) => ({
                        ...req,
                        id: req.id || `REQ-${String(index + 1).padStart(3, '0')}`,
                        review_status: req.review_status || 'pending',
                        reviewer_notes: req.reviewer_notes || ''
                    }));

                    filteredRequirements = [...allRequirements];
                    hasUnsavedChanges = false;
                    hasSavedRequirements = allRequirements.length > 0;
                    applyFiltersAndRender();
                    updateSaveState();
                } catch (error) {
                    container.innerHTML = `
                        <p style="text-align: center; color: #c33; padding: 40px;">
                            Failed to load extracted requirements: ${escapeHtml(error.message)}
                        </p>
                    `;
                }
            }

            // HTML Viewer function
            function showHtmlOutput(jobId) {
                if (!jobId || hasUnsavedChanges || !hasSavedRequirements) {
                    return;
                }
                currentJobId = jobId;
                const url = `/api/download/${jobId}/html_module`;
                window.open(url, '_blank');
            }
            
            document.getElementById('categoryFilter').addEventListener('change', applyFiltersAndRender);
            document.getElementById('priorityFilter').addEventListener('change', applyFiltersAndRender);
            document.getElementById('statusFilter').addEventListener('change', applyFiltersAndRender);
            document.getElementById('searchInput').addEventListener('input', applyFiltersAndRender);
            document.getElementById('confidenceFilter').addEventListener('input', (e) => {
                document.getElementById('confidenceValue').textContent = Number(e.target.value).toFixed(2);
                applyFiltersAndRender();
            });
            document.getElementById('acceptVisibleBtn').addEventListener('click', async () => {
                try {
                    await bulkUpdateVisible('accepted');
                } catch (error) {
                    errorDiv.textContent = `Update failed: ${error.message}`;
                    errorDiv.style.display = 'block';
                }
            });
            document.getElementById('rejectVisibleBtn').addEventListener('click', async () => {
                try {
                    await bulkUpdateVisible('rejected');
                } catch (error) {
                    errorDiv.textContent = `Update failed: ${error.message}`;
                    errorDiv.style.display = 'block';
                }
            });
            document.getElementById('resetFiltersBtn').addEventListener('click', resetFilters);

            // File input handler — update badge to show file count when multi-select
            fileInput.addEventListener('change', (e) => {
                const count = e.target.files.length;
                if (count === 1) {
                    fileName.textContent = e.target.files[0].name;
                    fileName.style.display = 'inline-block';
                } else if (count > 1) {
                    fileName.textContent = `${count} files selected`;
                    fileName.style.display = 'inline-block';
                } else {
                    fileName.style.display = 'none';
                }
            });
            
            document.getElementById('showHtmlOutputBtn').addEventListener('click', () => {
                showHtmlOutput(currentJobId);
            });

            uploadForm.addEventListener('submit', async (e) => {
                e.preventDefault();

                // Validate file selection
                if (!fileInput.files || fileInput.files.length === 0) {
                    errorDiv.textContent = 'Please select a file to upload';
                    errorDiv.style.display = 'block';
                    return;
                }

                const formData = new FormData();
                // Append ALL selected files under the key 'files' (matches FastAPI List[UploadFile])
                Array.from(fileInput.files).forEach(f => formData.append('files', f));
                formData.append('title', document.getElementById('title').value);
                formData.append('org_context_url', document.getElementById('orgContext').value || '');
                formData.append('min_confidence', document.getElementById('minConfidence').value);
                formData.append('is_sap_opp', document.getElementById('isSapOpp').value === 'true');
                
                analyzeBtn.disabled = true;
                analyzeBtn.textContent = '⏳ Analyzing...';
                progressContainer.style.display = 'block';
                results.style.display = 'none';
                errorDiv.style.display = 'none';
                progressText.textContent = 'PROCESSING';
                stepText.textContent = 'Submitting analysis job';
                statusDetailText.textContent = 'Uploading file and starting backend analysis';
                elapsedTimeText.textContent = 'Elapsed: 0s';
                analysisStartedAt = Date.now();
                currentJobId = null;
                allRequirements = [];
                filteredRequirements = [];
                hasUnsavedChanges = false;
                hasSavedRequirements = false;
                updateSaveState();
                
                try {
                    const controller = new AbortController();
                    // 120s — generous for large PDFs; the server still responds in <2s
                    // (it just saves the file and queues, analysis runs in background)
                    const timeoutId = setTimeout(() => controller.abort(), 120000);

                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData,
                        signal: controller.signal
                    });

                    clearTimeout(timeoutId);
                    stepText.textContent = 'Analysis job accepted by server';
                    statusDetailText.textContent = 'Polling backend status updates';

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.detail || 'Analysis failed');
                    }

                    // Poll for status
                    pollStatus(data.job_id);

                } catch (error) {
                    const message = error.name === 'AbortError'
                        ? 'Upload timed out. The server may need to be restarted. Run: uvicorn web_app:app --host 0.0.0.0 --port 8080 inside rfp-analyzer/'
                        : error.message;
                    errorDiv.textContent = `Error: ${message}`;
                    errorDiv.style.display = 'block';
                    analyzeBtn.disabled = false;
                    analyzeBtn.textContent = '🔍 Analyze';
                    progressContainer.style.display = 'none';
                }
            });
            
            async function pollStatus(jobId) {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/api/status/${jobId}`);
                        const status = await response.json();
                        
                        progressFill.style.width = `${status.progress}%`;
                        progressFill.textContent = `${status.progress}%`;
                        progressText.textContent = status.status.toUpperCase();
                        stepText.textContent = status.current_step || 'Processing';
                        statusDetailText.textContent = status.status_detail || '';
                        if (analysisStartedAt) {
                            const elapsedSeconds = Math.max(0, Math.floor((Date.now() - analysisStartedAt) / 1000));
                            elapsedTimeText.textContent = `Elapsed: ${elapsedSeconds}s`;
                        }
                        
                        if (status.status === 'completed') {
                            clearInterval(interval);
                            results.style.display = 'block';
                            statusDetailText.textContent = status.status_detail || 'Analysis completed successfully';

                            // Render Phase 0 conflict banner if applicable
                            currentPhase0Meta = status.phase0_meta || null;
                            renderPhase0Banner(currentPhase0Meta);

                            // Set download links for non-HTML files
                            document.getElementById('downloadMarkdown').href = `/api/download/${jobId}/markdown`;
                            document.getElementById('downloadExcel').href = `/api/download/${jobId}/excel`;
                            document.getElementById('downloadJson').href = `/api/download/${jobId}/json`;
                            setExportEnabled(false);

                            analyzeBtn.disabled = false;
                            analyzeBtn.textContent = '🔍 Analyze';

                            // Store current job ID for later use
                            currentJobId = jobId;
                            loadRequirements(jobId);
                        } else if (status.status === 'failed') {
                            clearInterval(interval);
                            errorDiv.textContent = `Analysis failed: ${status.error}`;
                            errorDiv.style.display = 'block';
                            analyzeBtn.disabled = false;
                            analyzeBtn.textContent = '🔍 Analyze';
                            progressContainer.style.display = 'none';
                        }
                    } catch (error) {
                        clearInterval(interval);
                        errorDiv.textContent = `Error checking status: ${error.message}`;
                        errorDiv.style.display = 'block';
                        analyzeBtn.disabled = false;
                        analyzeBtn.textContent = '🔍 Analyze';
                    }
                }, 1000);
            }
        </script>
    </body>
    </html>
    """)


class RequirementsUpdateRequest(BaseModel):
    requirements: list[dict[str, Any]]


@app.put("/api/requirements/{job_id}")
async def update_requirements(job_id: str, payload: RequirementsUpdateRequest):
    """Persist edited requirements into the running job state and regenerate exports."""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = analysis_jobs[job_id]
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")

    normalized_requirements = []
    for req in payload.requirements:
        normalized = Requirement.model_validate({
            **req,
            "category": req.get("category", Category.FUNCTIONAL),
            "priority": req.get("priority", Priority.MUST),
            "review_status": req.get("review_status", ReviewStatus.PENDING),
        })
        normalized_requirements.append(normalized.model_dump(mode="json"))

    job["requirements_state"] = normalized_requirements
    job["has_unsaved_changes"] = False
    print(f"[API] Saving reviewed requirements for job {job_id}: {len(normalized_requirements)} items")
    _persist_job_exports(job_id)
    print(f"[API] Export files regenerated for job {job_id}")

    return {
        "job_id": job_id,
        "saved": True,
        "requirements_count": len(normalized_requirements)
    }


@app.post("/api/analyze")
async def analyze_rfp(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    title: str = Form("RFP Analysis"),
    org_context_url: Optional[str] = Form(None),
    min_confidence: float = Form(0.0),
    is_sap_opp: bool = Form(False)
):
    """
    Upload and analyze one or more RFP documents.

    When multiple files are uploaded and Phase 0 is available, documents are
    first consolidated (classified, chunked, conflict-detected) before being
    handed to the multi-agent extraction pipeline.

    Args:
        files: One or more uploaded RFP files (PDF, DOCX, TXT)
        title: Analysis title
        org_context_url: Optional organizational context URL
        min_confidence: Minimum confidence threshold
        is_sap_opp: Enable SAP module mapping pass

    Returns:
        Job ID for tracking analysis progress
    """
    allowed_extensions = {'.pdf', '.docx', '.txt'}

    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Generate job ID and upload directory
    job_id = str(uuid.uuid4())
    upload_dir = Path("uploads") / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: List[Path] = []
    for upload in files:
        original_filename = Path(upload.filename or "uploaded_file").name
        file_ext = Path(original_filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
            )
        file_path = upload_dir / original_filename
        print(f"[API] /api/analyze saving file: {original_filename}")
        with open(file_path, "wb") as f:
            content = await upload.read()
            f.write(content)
        saved_paths.append(file_path)

    print(f"[API] Saved {len(saved_paths)} file(s) for job {job_id}")

    # Initialize job status
    analysis_jobs[job_id] = {
        "job_id": job_id,
        "status": "pending",
        "progress": 0,
        "current_step": "Queued",
        "status_detail": "Waiting for background worker to start",
        "result_url": None,
        "error": None,
        "started_at": datetime.now(),
        "completed_at": None,
        "file_paths": [str(p) for p in saved_paths],
        "title": title,
        "phase0_available": PHASE0_AVAILABLE,
        "phase0_meta": None,
    }

    # Start analysis in background
    print(f"[API] Queueing background analysis for job {job_id} ({len(saved_paths)} file(s))")
    background_tasks.add_task(
        run_analysis,
        job_id,
        saved_paths,
        title,
        org_context_url,
        min_confidence,
        is_sap_opp
    )

    log.info(
        "analysis_started",
        job_id=job_id,
        file_count=len(saved_paths),
        filenames=[p.name for p in saved_paths],
        is_sap_opp=is_sap_opp,
        phase0=PHASE0_AVAILABLE and len(saved_paths) > 1,
    )
    print(f"[API] Returning pending response for job {job_id}")

    return {
        "job_id": job_id,
        "status": "pending",
        "file_count": len(saved_paths),
        "phase0_enabled": PHASE0_AVAILABLE and len(saved_paths) > 1,
    }


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get analysis job status."""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return analysis_jobs[job_id]


@app.get("/api/download/{job_id}/{format}")
async def download_result(job_id: str, format: str):
    """Download analysis results."""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = analysis_jobs[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    if format == "markdown":
        file_path = job.get("markdown_path")
        media_type = "text/markdown"
    elif format == "excel":
        file_path = job.get("excel_path")
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif format == "json":
        file_path = job.get("json_path")
        media_type = "application/json"
    elif format == "html_category":
        file_path = job.get("html_category_path")
        media_type = "text/html"
    elif format == "html_module":
        file_path = job.get("html_module_path")
        media_type = "text/html"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: markdown, excel, json, html_category, html_module")
    
    if (not file_path or not Path(file_path).exists()) and format == "json":
        requirements = job.get("requirements_state")
        if requirements is not None:
            return requirements

    if not file_path or not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    # For HTML formats, serve inline (not as download) so iframe can display them
    if format in ["html_category", "html_module"]:
        return FileResponse(
            file_path,
            media_type=media_type,
            headers={"Content-Disposition": "inline"}  # Force inline display
        )
    else:
        # For other formats, serve as download with filename
        return FileResponse(
            file_path,
            media_type=media_type,
            filename=Path(file_path).name
        )


@app.get("/api/jobs")
async def list_jobs():
    """List all analysis jobs."""
    return {
        "jobs": [
            {
                "job_id": job_id,
                "status": job["status"],
                "title": job["title"],
                "started_at": job["started_at"].isoformat(),
                "completed_at": job["completed_at"].isoformat() if job["completed_at"] else None
            }
            for job_id, job in analysis_jobs.items()
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    Path("uploads").mkdir(exist_ok=True)
    Path("outputs/web").mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("[START] RFP Analyzer Web Interface")
    print("=" * 60)
    print()
    print("[URL] Server: http://localhost:8080")
    print("[DOCS] API Documentation: http://localhost:8080/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

# Made with Bob
