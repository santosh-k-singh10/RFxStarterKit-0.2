# RFP Analyzer Web Interface Guide

## Overview

The RFP Analyzer now includes a modern web interface that allows you to analyze RFP documents directly from your browser.

## Features

- 📤 **Drag & Drop Upload** - Easy file upload interface
- 📊 **Real-time Progress** - Live updates during analysis
- 🎨 **Modern UI** - Clean, responsive design
- 📥 **Multiple Export Formats** - Download results as Markdown or Excel
- 🔄 **Background Processing** - Non-blocking analysis
- 🌐 **Organizational Context** - Support for remote context URLs

## Installation

### 1. Install Web Dependencies

```bash
cd rfp-analyzer
pip install -r requirements_web.txt
```

This installs:
- FastAPI - Modern web framework
- Uvicorn - ASGI server
- python-multipart - File upload support
- aiofiles - Async file operations

### 2. Verify Installation

```bash
python -c "import fastapi; print('FastAPI installed successfully')"
```

## Running the Web Interface

### Quick Start

```bash
cd rfp-analyzer
python web_app.py
```

The server will start on `http://localhost:8080`

### Custom Port

```bash
# Run on a different port
python -c "import uvicorn; from web_app import app; uvicorn.run(app, host='0.0.0.0', port=3000)"
```

### Production Mode

```bash
# With more workers for production
uvicorn web_app:app --host 0.0.0.0 --port 8080 --workers 4
```

## Using the Web Interface

### 1. Access the Interface

Open your browser and navigate to:
```
http://localhost:8080
```

### 2. Upload an RFP Document

1. Click the upload area or drag & drop a file
2. Supported formats: PDF, DOCX, TXT
3. The filename will appear once selected

### 3. Configure Analysis

**Analysis Title** (required)
- Default: "RFP Analysis"
- Used for naming output files

**Organizational Context URL** (optional)
- Local file: `org_context/config/org_config.yaml`
- SharePoint: `https://company.sharepoint.com/.../org_config.yaml`
- OneDrive: `https://company-my.sharepoint.com/.../org_config.yaml`
- HTTP: `https://config.company.com/org_config.yaml`
- S3: `s3://bucket/path/org_config.yaml`

**Minimum Confidence** (optional)
- Range: 0.0 to 1.0
- Default: 0.0 (include all requirements)
- Higher values filter out low-confidence requirements

### 4. Start Analysis

Click the **"Analyze RFP"** button to start processing.

### 5. Monitor Progress

The interface shows:
- **Progress Bar** - Visual progress indicator (0-100%)
- **Current Step** - What the system is currently doing
- **Status** - Overall status (PENDING, PROCESSING, COMPLETED, FAILED)

Analysis steps:
1. Loading organizational context (5%)
2. Ingesting document (10%)
3. Extracting functional requirements (25%)
4. Extracting non-functional requirements (40%)
5. Extracting compliance requirements (55%)
6. Detecting ambiguities (70%)
7. Assessing risks (85%)
8. Synthesizing results (95%)
9. Generating reports (98%)
10. Complete (100%)

### 6. Download Results

Once complete, two download buttons appear:
- **📄 Download Markdown** - Human-readable report
- **📊 Download Excel** - Structured data for further analysis

## API Endpoints

The web interface also provides a REST API:

### POST /api/analyze

Upload and analyze an RFP document.

**Request:**
```bash
curl -X POST http://localhost:8080/api/analyze \
  -F "file=@rfp.pdf" \
  -F "title=My RFP Analysis" \
  -F "org_context_url=https://sharepoint.com/.../org_config.yaml" \
  -F "min_confidence=0.0"
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

### GET /api/status/{job_id}

Check analysis status.

**Request:**
```bash
curl http://localhost:8080/api/status/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "current_step": "Extracting non-functional requirements",
  "result_url": null,
  "error": null,
  "started_at": "2026-04-12T00:30:00",
  "completed_at": null
}
```

### GET /api/download/{job_id}/{format}

Download analysis results.

**Formats:**
- `markdown` - Markdown report
- `excel` - Excel workbook

**Request:**
```bash
# Download Markdown
curl -O http://localhost:8080/api/download/550e8400-e29b-41d4-a716-446655440000/markdown

# Download Excel
curl -O http://localhost:8080/api/download/550e8400-e29b-41d4-a716-446655440000/excel
```

### GET /api/jobs

List all analysis jobs.

**Request:**
```bash
curl http://localhost:8080/api/jobs
```

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "title": "My RFP Analysis",
      "started_at": "2026-04-12T00:30:00",
      "completed_at": "2026-04-12T00:32:15"
    }
  ]
}
```

### GET /docs

Interactive API documentation (Swagger UI).

```
http://localhost:8080/docs
```

## File Structure

```
rfp-analyzer/
├── web_app.py              # FastAPI web server
├── uploads/                # Uploaded RFP files (auto-created)
│   └── {job_id}/
│       └── rfp.pdf
└── outputs/
    └── web/                # Analysis results (auto-created)
        └── {job_id}/
            ├── analysis.md
            └── analysis.xlsx
```

## Environment Variables

Set these for remote context loading:

```bash
# SharePoint
export SHAREPOINT_CLIENT_ID="..."
export SHAREPOINT_CLIENT_SECRET="..."
export SHAREPOINT_TENANT_ID="..."

# OneDrive
export ONEDRIVE_ACCESS_TOKEN="..."

# Box
export BOX_ACCESS_TOKEN="..."

# S3
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
```

## Troubleshooting

### Port Already in Use

If port 8080 is already in use:

```bash
# Use a different port
python -c "import uvicorn; from web_app import app; uvicorn.run(app, host='0.0.0.0', port=8081)"
```

### Import Errors

If you see import errors:

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements_web.txt
```

### File Upload Fails

Check file size limits. By default, FastAPI allows up to 100MB uploads.

To increase:

```python
# In web_app.py, add:
app.add_middleware(
    CORSMiddleware,
    max_upload_size=500 * 1024 * 1024  # 500MB
)
```

### Analysis Hangs

Check the terminal for error messages. Common issues:
- Missing API keys (ANTHROPIC_API_KEY)
- Network connectivity
- Insufficient memory for large documents

### Results Not Downloading

Ensure the analysis completed successfully:
1. Check status endpoint: `/api/status/{job_id}`
2. Verify status is "completed"
3. Check for error messages

## Security Considerations

### Production Deployment

For production use:

1. **Enable HTTPS**
```bash
uvicorn web_app:app --host 0.0.0.0 --port 443 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

2. **Add Authentication**
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/analyze")
async def analyze_rfp(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    ...
):
    # Verify token
    verify_token(credentials.credentials)
    ...
```

3. **Rate Limiting**
```bash
pip install slowapi

from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/analyze")
@limiter.limit("5/minute")
async def analyze_rfp(...):
    ...
```

4. **File Size Limits**
```python
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@app.post("/api/analyze")
async def analyze_rfp(file: UploadFile = File(...)):
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    ...
```

### Network Security

- Run behind a reverse proxy (nginx, Apache)
- Use firewall rules to restrict access
- Enable CORS only for trusted domains
- Implement request logging and monitoring

## Performance Tips

### 1. Use Multiple Workers

```bash
uvicorn web_app:app --workers 4
```

### 2. Enable Caching

Cache organizational context:

```python
from functools import lru_cache

@lru_cache(maxsize=10)
def load_org_context(url: str):
    return initialize_context_manager(url)
```

### 3. Cleanup Old Jobs

Periodically clean up old analysis jobs:

```python
import time
from datetime import datetime, timedelta

def cleanup_old_jobs():
    cutoff = datetime.now() - timedelta(days=7)
    for job_id, job in list(analysis_jobs.items()):
        if job["started_at"] < cutoff:
            # Delete files
            shutil.rmtree(f"uploads/{job_id}", ignore_errors=True)
            shutil.rmtree(f"outputs/web/{job_id}", ignore_errors=True)
            # Remove from memory
            del analysis_jobs[job_id]
```

## Integration with Existing Tools

### Use with CLI

The web interface and CLI can run simultaneously:

```bash
# Terminal 1: Web interface
python web_app.py

# Terminal 2: CLI
python main.py rfp.pdf --org-context org_context/config/org_config.yaml
```

### Use with MCP Gateway

If you have mcpgateway running, the web interface can use it:

```python
# In web_app.py, configure to use gateway
MCP_GATEWAY_URL = "http://localhost:8000"
```

## Support

For issues or questions:
- Check the troubleshooting section above
- Review terminal logs for error messages
- Consult the main README.md for general setup
- See REMOTE_CONTEXT_GUIDE.md for context loading issues