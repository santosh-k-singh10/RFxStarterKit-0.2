# API Reference

REST endpoints exposed by the RFP Analyzer (`web_app.py`, default port **8080**).

---

## Analysis

### `POST /api/analyze`

Upload one or more documents and start an analysis job.

**Form data:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `files` | `File[]` | ✅ | PDF, DOCX, TXT, MD, XLSX, or CSV |
| `title` | `string` | | Analysis title (default: `"RFP Analysis"`) |
| `org_context_url` | `string` | | URL to organisational context YAML/JSON |
| `min_confidence` | `float` | | Filter threshold 0.0–1.0 (default: `0.0`) |

**Response `202`:**
```json
{
  "job_id": "3f2d1a...",
  "status": "pending",
  "message": "Analysis started for 2 file(s)"
}
```

---

### `GET /api/status/{job_id}`

Poll analysis progress.

**Response `200`:**
```json
{
  "job_id": "3f2d1a...",
  "status": "processing",
  "progress": 65,
  "current_step": "Extracting compliance requirements",
  "status_detail": "Running compliance extraction across 38 chunks",
  "phase0_metadata": {
    "rfp_id": "RFP-ABC123",
    "documents": [{"name": "rfp.pdf", "type": "rfp", "chunks": 38}],
    "conflicts_detected": 1
  }
}
```

`status` values: `pending` → `processing` → `completed` | `failed`

---

### `GET /api/results/{job_id}`

Retrieve completed results.

**Response `200`:**
```json
{
  "job_id": "3f2d1a...",
  "title": "NHS Portal RFP",
  "requirements": [
    {
      "id": "FR-001",
      "title": "User authentication",
      "description": "...",
      "category": "functional",
      "priority": "must",
      "confidence": 0.92,
      "ambiguity_flag": false,
      "source_section": "3.1",
      "clarification_questions": []
    }
  ],
  "phase0_metadata": { "...": "..." },
  "exports": {
    "markdown": "/api/download/3f2d1a.../markdown",
    "excel": "/api/download/3f2d1a.../excel",
    "json": "/api/download/3f2d1a.../json",
    "html_category": "/api/download/3f2d1a.../html_category",
    "html_module": "/api/download/3f2d1a.../html_module"
  }
}
```

---

### `GET /api/download/{job_id}/{file_type}`

Download an exported file.

**`file_type` options:** `markdown` · `excel` · `json` · `html_category` · `html_module`

Returns the file with appropriate `Content-Type` and `Content-Disposition: attachment` headers.

---

## Health

### `GET /`

Returns `200 OK` (HTML web interface). Used for container healthchecks.

### `GET /api/jobs`

Returns the list of all in-memory job IDs and their current status. Useful for liveness checks.

---

## Phase 0 (standalone)

```bash
cd document-consolidator/phase0_router
uvicorn phase0.api:app --reload
```

### `POST /phase0/analyze`

Upload multiple documents for classification and conflict detection.

**Response `200`:**
```json
{
  "success": true,
  "rfp_id": "RFP-ABC123",
  "document_context": {
    "documents": [
      { "name": "rfp.pdf", "type": "rfp", "chunks": 45 },
      { "name": "compliance.docx", "type": "compliance", "chunks": 12 }
    ],
    "phase_contexts": { "phase1": "...", "phase2": "..." },
    "conflicts": [
      { "description": "Delivery date conflict between rfp.pdf §4 and compliance.docx §2" }
    ],
    "metadata": { "total_chunks": 57, "processing_time_s": 8.3 }
  },
  "warnings": []
}
```

---

## Programmatic usage (Python)

```python
from rfp_analyzer.main import run_analysis

result = run_analysis(
    file_path="rfp.pdf",
    title="NHS Portal RFP",
    output_dir="./results",
)

for req in result["requirements"]:
    print(req.id, req.category, req.title)

print("Excel:", result["excel_path"])
```
