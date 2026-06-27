"""
web_app_enhanced.py
-------------------
Enhanced FastAPI web interface for RFP Analyzer with collapsible HTML output viewer.

Provides a browser-based UI for uploading RFP documents and viewing analysis results
with a fixed bottom panel showing HTML output that can be expanded/collapsed.

Usage:
    python web_app_enhanced.py
    
Then open: http://localhost:8080
"""

from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

import structlog
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import RFP analyzer components
from core.ingestor import ingest_document
from core.schemas import AnalysisState
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

log = structlog.get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RFP Analyzer Enhanced",
    description="AI-powered RFP analysis with multi-agent system and HTML preview",
    version="2.1.0"
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


async def run_analysis(
    job_id: str,
    file_path: Path,
    title: str,
    org_context_url: Optional[str] = None,
    min_confidence: float = 0.0,
    is_sap_opp: bool = False
):
    """
    Run RFP analysis in background.
    
    Args:
        job_id: Unique job identifier
        file_path: Path to uploaded RFP file
        title: Analysis title
        org_context_url: Optional organizational context URL
        min_confidence: Minimum confidence threshold
    """
    try:
        # Update status
        analysis_jobs[job_id]["status"] = "processing"
        analysis_jobs[job_id]["current_step"] = "Loading organizational context"
        analysis_jobs[job_id]["progress"] = 5
        
        # Load organizational context if provided
        if org_context_url:
            try:
                initialize_context_manager(org_context_url)
                log.info("org_context_loaded", url=org_context_url)
            except Exception as e:
                log.warning("org_context_load_failed", error=str(e))
        
        # Step 1: Ingest document
        analysis_jobs[job_id]["current_step"] = "Ingesting document"
        analysis_jobs[job_id]["progress"] = 10
        
        state = AnalysisState(file_path=str(file_path))
        state.metadata.update({
            "title": title,
            "min_confidence": min_confidence,
        })
        
        state.chunks = ingest_document(state.file_path)
        state.document_text = "\n\n".join(chunk.text for chunk in state.chunks)
        log.info("document_ingested", chunks=len(state.chunks))
        
        # Step 2: Extract functional requirements
        analysis_jobs[job_id]["current_step"] = "Extracting functional requirements"
        analysis_jobs[job_id]["progress"] = 25
        
        state.functional = extract_functional(state.chunks)
        if min_confidence > 0.0:
            state.functional = [
                req for req in state.functional if req.confidence >= min_confidence
            ]
        log.info("functional_extracted", count=len(state.functional))
        
        # Step 3: Extract non-functional requirements
        analysis_jobs[job_id]["current_step"] = "Extracting non-functional requirements"
        analysis_jobs[job_id]["progress"] = 40
        
        state.non_functional = extract_nonfunctional(state.chunks)
        if min_confidence > 0.0:
            state.non_functional = [
                req for req in state.non_functional if req.confidence >= min_confidence
            ]
        log.info("nonfunctional_extracted", count=len(state.non_functional))
        
        # Step 4: Extract compliance requirements
        analysis_jobs[job_id]["current_step"] = "Extracting compliance requirements"
        analysis_jobs[job_id]["progress"] = 55
        
        state.compliance = extract_compliance(state.chunks)
        if min_confidence > 0.0:
            state.compliance = [
                req for req in state.compliance if req.confidence >= min_confidence
            ]
        log.info("compliance_extracted", count=len(state.compliance))
        
        # Step 5: Detect ambiguities
        analysis_jobs[job_id]["current_step"] = "Detecting ambiguities"
        analysis_jobs[job_id]["progress"] = 70
        
        state.ambiguities = extract_ambiguities(state.chunks)
        if min_confidence > 0.0:
            state.ambiguities = [
                req for req in state.ambiguities if req.confidence >= min_confidence
            ]
        log.info("ambiguities_detected", count=len(state.ambiguities))
        
        # Step 6: Assess risks
        analysis_jobs[job_id]["current_step"] = "Assessing risks"
        analysis_jobs[job_id]["progress"] = 85
        
        state.risks = extract_risks(state.chunks)
        if min_confidence > 0.0:
            state.risks = [
                req for req in state.risks if req.confidence >= min_confidence
            ]
        log.info("risks_assessed", count=len(state.risks))
        
        # Step 7: Synthesize results
        analysis_jobs[job_id]["current_step"] = "Synthesizing results"
        analysis_jobs[job_id]["progress"] = 95
        
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
        
        # Step 8: Export results
        analysis_jobs[job_id]["current_step"] = "Generating reports"
        analysis_jobs[job_id]["progress"] = 98
        
        output_dir = Path("outputs") / "web" / job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        safe_title = "".join(ch if ch.isalnum() or ch in (" ", "-", "_") else "_" for ch in title).strip() or "RFP_Analysis"
        md_path = output_dir / f"{safe_title.replace(' ', '_')}.md"
        xlsx_path = output_dir / f"{safe_title.replace(' ', '_')}.xlsx"
        json_path = output_dir / f"{safe_title.replace(' ', '_')}.json"
        html_category_path = output_dir / f"{safe_title.replace(' ', '_')}_by_category.html"
        html_module_path = output_dir / f"{safe_title.replace(' ', '_')}_by_module.html"
        
        export_markdown(state.final_requirements, str(md_path), rfp_title=title)
        export_excel(state.final_requirements, str(xlsx_path))
        export_json(state.final_requirements, str(json_path), rfp_title=title)
        export_html(state.final_requirements, str(html_category_path), rfp_title=title)
        export_html_by_module(state.final_requirements, str(html_module_path), rfp_title=title)
        
        # Update status to completed
        analysis_jobs[job_id]["status"] = "completed"
        analysis_jobs[job_id]["progress"] = 100
        analysis_jobs[job_id]["current_step"] = "Analysis complete"
        analysis_jobs[job_id]["result_url"] = f"/api/results/{job_id}"
        analysis_jobs[job_id]["completed_at"] = datetime.now()
        analysis_jobs[job_id]["markdown_path"] = str(md_path)
        analysis_jobs[job_id]["excel_path"] = str(xlsx_path)
        analysis_jobs[job_id]["json_path"] = str(json_path)
        analysis_jobs[job_id]["html_category_path"] = str(html_category_path)
        analysis_jobs[job_id]["html_module_path"] = str(html_module_path)
        
        log.info("analysis_completed", job_id=job_id)
        
    except Exception as e:
        log.error("analysis_failed", job_id=job_id, error=str(e))
        analysis_jobs[job_id]["status"] = "failed"
        analysis_jobs[job_id]["error"] = str(e)
        analysis_jobs[job_id]["completed_at"] = datetime.now()


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the enhanced web interface with collapsible HTML output viewer."""
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>RFP Analyzer Enhanced</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            display: grid;
            grid-template-columns: 360px 1fr;
            height: 100vh;
            overflow: hidden;
        }
        
        /* Left Panel */
        .left-panel {
            background: white;
            border-right: 0.5px solid #e0e0e0;
            overflow-y: auto;
            padding: 24px;
        }
        
        h1 {
            color: #1a1a1a;
            margin-bottom: 8px;
            font-size: 1.5em;
            font-weight: 700;
        }
        
        .subtitle {
            color: #666;
            margin-bottom: 24px;
            font-size: 0.875em;
        }
        
        .upload-area {
            border: 2px dashed #d0d0d0;
            border-radius: 8px;
            padding: 24px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .upload-area:hover {
            background: #fafafa;
            border-color: #667eea;
        }
        
        .upload-icon {
            font-size: 2.5em;
            margin-bottom: 12px;
            color: #999;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        label {
            display: block;
            margin-bottom: 6px;
            color: #555;
            font-weight: 600;
            font-size: 0.75em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        input[type="text"], input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            font-size: 0.875em;
            transition: border-color 0.2s;
        }
        
        input[type="text"]:focus, input[type="number"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 6px;
            font-size: 0.875em;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            width: 100%;
        }
        
        button:hover {
            background: #5568d3;
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        /* Status Card */
        .status-card {
            display: none;
            margin-top: 20px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        
        .status-card.show {
            display: block;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 12px;
        }
        
        .progress-fill {
            height: 100%;
            background: #667eea;
            transition: width 0.3s;
        }
        
        .progress-text {
            font-size: 0.75em;
            color: #666;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .step-text {
            font-size: 0.75em;
            color: #999;
        }
        
        /* Stats Grid */
        .stats-grid {
            display: none;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 16px;
        }
        
        .stats-grid.show {
            display: grid;
        }
        
        .stat-card {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 4px;
        }
        
        .stat-label {
            font-size: 0.7em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }
        
        .download-links {
            display: none;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #e0e0e0;
        }
        
        .download-links.show {
            display: block;
        }
        
        .download-btn {
            display: block;
            margin-bottom: 8px;
            padding: 10px;
            background: #f8f9fa;
            color: #667eea;
            text-decoration: none;
            border-radius: 6px;
            font-size: 0.875em;
            font-weight: 600;
            text-align: center;
            transition: background 0.2s;
        }
        
        .download-btn:hover {
            background: #e9ecef;
        }
        
        .error {
            display: none;
            margin-top: 16px;
            padding: 12px;
            background: #fee;
            border: 1px solid #fcc;
            border-radius: 6px;
            color: #c33;
            font-size: 0.875em;
        }
        
        .error.show {
            display: block;
        }
        
        /* Right Panel */
        .right-panel {
            background: #fafafa;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
        
        .right-header {
            background: white;
            border-bottom: 0.5px solid #e0e0e0;
            padding: 20px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .right-header h2 {
            font-size: 1.25em;
            font-weight: 700;
            color: #1a1a1a;
        }
        
        .view-toggle {
            display: flex;
            gap: 0;
            background: #f0f0f0;
            border-radius: 6px;
            padding: 2px;
        }
        
        .view-btn {
            padding: 6px 16px;
            border: none;
            background: transparent;
            color: #666;
            font-size: 0.75em;
            font-weight: 600;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s;
            width: auto;
        }
        
        .view-btn.active {
            background: white;
            color: #1a1a1a;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        /* Tab Bar */
        .tab-bar {
            background: white;
            border-bottom: 0.5px solid #e0e0e0;
            padding: 0 24px;
            display: flex;
            gap: 0;
        }
        
        .tab {
            padding: 12px 20px;
            border: none;
            background: transparent;
            color: #666;
            font-size: 0.875em;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
            width: auto;
        }
        
        .tab:hover {
            color: #1a1a1a;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        /* Content Area */
        .content-area {
            padding: 24px;
            flex: 1;
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }
        
        .empty-state-icon {
            font-size: 4em;
            margin-bottom: 16px;
            opacity: 0.3;
        }
        
        /* Category Accordion */
        .category-section {
            margin-bottom: 16px;
            background: white;
            border-radius: 8px;
