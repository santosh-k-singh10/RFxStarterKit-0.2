"""
phase0/api.py
FastAPI endpoint for Phase 0 Document Router Agent.

Endpoint: POST /phase0/analyze
Accepts:  multipart/form-data with key "documents" (multiple files)
Returns:  Phase0Response JSON

Run with:
    uvicorn phase0.api:app --reload --port 8001
"""

from __future__ import annotations
import logging
import shutil
import tempfile
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .router import Phase0Router
from .schema import Phase0Response

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RFP Analyzer — Phase 0 Document Router",
    description="Classifies, chunks, and routes multi-document RFP packs into structured context for downstream phases.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten in production
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Supported upload extensions
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".xlsx", ".csv"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Phase 0 Document Router</title>
        <style>
            :root {
                --bg: #f3f4f6;
                --panel: #ffffff;
                --border: #d1d5db;
                --text: #111827;
                --muted: #6b7280;
                --primary: #2563eb;
                --primary-dark: #1d4ed8;
                --success-bg: #ecfdf5;
                --success-border: #a7f3d0;
                --warn-bg: #fff7ed;
                --warn-border: #fdba74;
                --error-bg: #fef2f2;
                --error-border: #fca5a5;
            }
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: var(--bg);
                color: var(--text);
            }
            .page {
                max-width: 1100px;
                margin: 24px auto;
                padding: 0 16px;
            }
            .panel {
                background: var(--panel);
                border: 1px solid var(--border);
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
            }
            .toolbar {
                display: flex;
                gap: 12px;
                align-items: center;
                padding: 14px 16px;
                border-bottom: 1px solid var(--border);
                flex-wrap: wrap;
            }
            .toolbar-label {
                font-size: 14px;
                color: var(--muted);
                font-weight: 600;
                min-width: 110px;
            }
            .btn {
                border: 1px solid #c7cdd4;
                background: #fff;
                color: var(--text);
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 14px;
                cursor: pointer;
            }
            .btn:hover { border-color: var(--primary); }
            .btn-primary {
                background: var(--primary);
                color: #fff;
                border-color: var(--primary);
            }
            .btn-primary:hover {
                background: var(--primary-dark);
                border-color: var(--primary-dark);
            }
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .input, .number {
                border: 1px solid #c7cdd4;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                background: #fff;
            }
            .input {
                min-width: 220px;
            }
            .number {
                width: 90px;
            }
            .content {
                padding: 16px;
            }
            .hint {
                color: var(--muted);
                font-size: 13px;
                margin-bottom: 12px;
            }
            .file-list {
                margin: 0 0 16px 0;
                padding-left: 18px;
            }
            .status, .box {
                border-radius: 8px;
                padding: 12px 14px;
                margin-top: 14px;
                border: 1px solid var(--border);
                background: #fff;
            }
            .status { display: none; }
            .status.info { display: block; }
            .status.success {
                display: block;
                background: var(--success-bg);
                border-color: var(--success-border);
            }
            .status.error {
                display: block;
                background: var(--error-bg);
                border-color: var(--error-border);
            }
            .box.warn {
                background: var(--warn-bg);
                border-color: var(--warn-border);
            }
            .box h3 {
                margin: 0 0 10px 0;
                font-size: 16px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
            }
            th, td {
                text-align: left;
                padding: 10px 8px;
                border-bottom: 1px solid #e5e7eb;
                font-size: 14px;
                vertical-align: top;
            }
            code {
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
            }
            .links {
                margin-top: 14px;
                font-size: 14px;
            }
            .links a {
                color: var(--primary);
                text-decoration: none;
                margin-right: 14px;
            }
            .links a:hover { text-decoration: underline; }
            pre {
                white-space: pre-wrap;
                word-break: break-word;
                background: #0f172a;
                color: #e5e7eb;
                padding: 14px;
                border-radius: 8px;
                overflow: auto;
                max-height: 420px;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="page">
            <div class="panel">
                <div class="toolbar">
                    <div class="toolbar-label">📄 Upload RFP</div>
                    <input id="fileInput" type="file" multiple accept=".pdf,.docx,.txt,.md,.xlsx,.csv" style="display:none" />
                    <button class="btn" onclick="document.getElementById('fileInput').click()">Choose File</button>
                    <input id="domainInput" class="input" type="text" placeholder="Domain (optional)" />
                    <input id="scoreInput" class="number" type="number" step="0.1" min="0" value="0.0" />
                    <button id="analyzeBtn" class="btn btn-primary" disabled>Analyze</button>
                </div>

                <div class="content">
                    <div class="hint">
                        Supported formats: <code>.pdf</code>, <code>.docx</code>, <code>.txt</code>, <code>.md</code>, <code>.xlsx</code>, <code>.csv</code>.
                        You can select one or more files.
                    </div>

                    <div id="selectedFilesWrap" style="display:none;">
                        <h3>Selected files</h3>
                        <ul id="selectedFiles" class="file-list"></ul>
                    </div>

                    <div id="statusBox" class="status"></div>

                    <div id="summaryBox" class="box" style="display:none;">
                        <h3>Document classification summary</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>File</th>
                                    <th>Type</th>
                                    <th>Confidence</th>
                                    <th>Pages</th>
                                    <th>Review</th>
                                </tr>
                            </thead>
                            <tbody id="summaryBody"></tbody>
                        </table>
                    </div>

                    <div id="conflictsBox" class="box warn" style="display:none;">
                        <h3>Conflicts</h3>
                        <ul id="conflictsList" class="file-list"></ul>
                    </div>

                    <div id="responseBox" class="box" style="display:none;">
                        <h3>Raw response</h3>
                        <pre id="responsePre"></pre>
                    </div>

                    <div class="links">
                        <a href="/docs" target="_blank" rel="noreferrer">Swagger UI</a>
                        <a href="/health" target="_blank" rel="noreferrer">Health check</a>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const fileInput = document.getElementById('fileInput');
            const analyzeBtn = document.getElementById('analyzeBtn');
            const selectedFilesWrap = document.getElementById('selectedFilesWrap');
            const selectedFiles = document.getElementById('selectedFiles');
            const statusBox = document.getElementById('statusBox');
            const summaryBox = document.getElementById('summaryBox');
            const summaryBody = document.getElementById('summaryBody');
            const conflictsBox = document.getElementById('conflictsBox');
            const conflictsList = document.getElementById('conflictsList');
            const responseBox = document.getElementById('responseBox');
            const responsePre = document.getElementById('responsePre');

            function setStatus(message, type = 'info') {
                statusBox.className = `status ${type}`;
                statusBox.textContent = message;
            }

            function renderSelectedFiles(files) {
                selectedFiles.innerHTML = '';
                if (!files.length) {
                    selectedFilesWrap.style.display = 'none';
                    analyzeBtn.disabled = true;
                    return;
                }

                files.forEach(file => {
                    const li = document.createElement('li');
                    li.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
                    selectedFiles.appendChild(li);
                });

                selectedFilesWrap.style.display = 'block';
                analyzeBtn.disabled = false;
            }

            function renderSummary(data) {
                const docs = data.document_context?.documents || [];
                summaryBody.innerHTML = '';

                docs.forEach(doc => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${doc.filename}</td>
                        <td><code>${doc.doc_type}</code></td>
                        <td>${Math.round((doc.confidence || 0) * 100)}%</td>
                        <td>${doc.pages ?? ''}</td>
                        <td>${doc.needs_review ? 'Yes' : 'No'}</td>
                    `;
                    summaryBody.appendChild(row);
                });

                summaryBox.style.display = docs.length ? 'block' : 'none';
            }

            function renderConflicts(data) {
                const conflicts = data.document_context?.conflicts || [];
                conflictsList.innerHTML = '';

                conflicts.forEach(conflict => {
                    const li = document.createElement('li');
                    li.innerHTML = `<strong>${conflict.severity}</strong>: ${conflict.description}`;
                    conflictsList.appendChild(li);
                });

                conflictsBox.style.display = conflicts.length ? 'block' : 'none';
            }

            fileInput.addEventListener('change', () => {
                renderSelectedFiles(Array.from(fileInput.files || []));
                summaryBox.style.display = 'none';
                conflictsBox.style.display = 'none';
                responseBox.style.display = 'none';
                setStatus('Files selected. Ready to analyze.', 'info');
            });

            analyzeBtn.addEventListener('click', async () => {
                const files = Array.from(fileInput.files || []);
                if (!files.length) {
                    setStatus('Select at least one file.', 'error');
                    return;
                }

                analyzeBtn.disabled = true;
                setStatus('Uploading files and running Phase 0 analysis...', 'info');

                try {
                    const formData = new FormData();
                    files.forEach(file => formData.append('documents', file));

                    const response = await fetch('/phase0/analyze', {
                        method: 'POST',
                        body: formData
                    });

                    const rawText = await response.text();
                    let data = null;

                    try {
                        data = JSON.parse(rawText);
                    } catch {
                        if (!response.ok) {
                            throw new Error(rawText || 'Phase 0 analysis failed.');
                        }
                        throw new Error('Server returned a non-JSON response.');
                    }

                    if (!response.ok) {
                        throw new Error(data.detail || 'Phase 0 analysis failed.');
                    }

                    renderSummary(data);
                    renderConflicts(data);
                    responsePre.textContent = JSON.stringify(data, null, 2);
                    responseBox.style.display = 'block';

                    const warnings = data.warnings || [];
                    const warningText = warnings.length ? ` Warnings: ${warnings.join(' | ')}` : '';
                    setStatus(`Analysis complete. RFP ID: ${data.rfp_id}.${warningText}`, 'success');
                } catch (error) {
                    setStatus(error.message || 'Unexpected error during analysis.', 'error');
                } finally {
                    analyzeBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """


@app.get("/health")
def health():
    return {"status": "ok", "phase": 0}


@app.post("/phase0/analyze", response_model=Phase0Response)
async def analyze_documents(
    documents: List[UploadFile] = File(..., description="RFP pack — upload multiple files"),
):
    """
    Accepts a multi-document RFP pack, runs Phase 0 pipeline, returns DocumentContext.

    Steps internally:
    1. Validate file types
    2. Save uploads to a temp directory
    3. Run Phase0Router
    4. Return Phase0Response with full DocumentContext
    """
    if not documents:
        raise HTTPException(status_code=400, detail="No documents uploaded.")

    warnings: List[str] = []

    # Validate extensions
    for upload in documents:
        filename = upload.filename or "uploaded_file"
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=415,
                detail=f"Unsupported file type '{suffix}' for {filename}. "
                       f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

    # Save uploads to temp dir
    tmpdir = tempfile.mkdtemp(prefix="phase0_")
    try:
        saved_paths: List[str | Path] = []
        for upload in documents:
            filename = upload.filename or "uploaded_file"
            dest = Path(tmpdir) / filename
            with dest.open("wb") as f:
                shutil.copyfileobj(upload.file, f)
            upload.file.close()
            saved_paths.append(dest)
            logger.info(f"Saved upload: {filename} ({upload.size or '?'} bytes)")

        # Run Phase 0 pipeline
        try:
            router = Phase0Router()
            doc_context = router.run(saved_paths)
        except Exception as e:
            logger.error(f"Phase 0 pipeline error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Phase 0 pipeline failed: {e}")
    finally:
        try:
            shutil.rmtree(tmpdir)
        except PermissionError:
            logger.warning(f"Could not delete temp directory immediately: {tmpdir}")
        except OSError as cleanup_error:
            logger.warning(f"Temp directory cleanup issue for {tmpdir}: {cleanup_error}")

    # Surface any low-confidence docs as warnings
    for doc in doc_context.documents:
        if doc.needs_review:
            warnings.append(
                f"Low classification confidence for '{doc.filename}' "
                f"({doc.confidence:.0%}) — please verify doc_type."
            )

    return Phase0Response(
        success=True,
        rfp_id=doc_context.rfp_id,
        document_context=doc_context,
        warnings=warnings,
    )
