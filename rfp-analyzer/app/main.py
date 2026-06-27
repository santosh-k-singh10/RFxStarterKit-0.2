"""
app/main.py
-----------
Main FastAPI application entry point.

Run with:
    uvicorn app.main:app --reload --port 8000
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import structlog

from app.routers import (
    analysis,
    requirements,
    clarifications,
    architecture,
    solution_mapping,
    exports
)

# Setup logging
from logging_config import setup_logging
setup_logging(
    log_file="./logs/web_app.log",
    console_level="INFO",
    file_level="DEBUG"
)

log = structlog.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RFP Analyzer - Enhanced Web Application",
    description="AI-powered RFP analysis with multi-agent system and interactive review interface",
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

# Mount static files (will be created in next phase)
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates (will be created in next phase)
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path)) if templates_path.exists() else None

# Include routers
app.include_router(analysis.router)
app.include_router(requirements.router)
app.include_router(clarifications.router)
app.include_router(architecture.router)
app.include_router(solution_mapping.router)
app.include_router(exports.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the home page."""
    if templates:
        return templates.TemplateResponse("home.html", {"request": request})
    return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RFP Analyzer</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; }
                .status { padding: 20px; background: #e8f5e9; border-left: 4px solid #4caf50; margin: 20px 0; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 RFP Analyzer - Enhanced Web Application</h1>
                <div class="status">
                    <p><strong>✅ API Server Running</strong></p>
                    <p>The backend API is operational. Frontend templates are being set up.</p>
                </div>
                <h2>Available Endpoints:</h2>
                <ul>
                    <li><a href="/docs">📚 API Documentation (Swagger UI)</a></li>
                    <li><a href="/redoc">📖 API Documentation (ReDoc)</a></li>
                </ul>
                <h2>API Routes:</h2>
                <ul>
                    <li><strong>POST /api/analyze</strong> - Upload and analyze RFP</li>
                    <li><strong>GET /api/status/{session_id}</strong> - Check analysis status</li>
                    <li><strong>GET /api/requirements</strong> - Get requirements (with filters)</li>
                    <li><strong>PATCH /api/requirements/{req_id}</strong> - Update requirement</li>
                    <li><strong>POST /api/clarifications/{req_id}/answer</strong> - Submit clarification answer</li>
                    <li><strong>POST /api/architecture/diagram</strong> - Generate architecture diagram</li>
                    <li><strong>POST /api/solution-mapping</strong> - Map to solutions</li>
                    <li><strong>GET /api/export/excel</strong> - Export to Excel</li>
                    <li><strong>GET /api/export/markdown</strong> - Export to Markdown</li>
                    <li><strong>GET /api/export/json</strong> - Export to JSON</li>
                </ul>
            </div>
        </body>
        </html>
    """)


@app.get("/review", response_class=HTMLResponse)
async def review(request: Request):
    """Serve the review page."""
    if templates:
        return templates.TemplateResponse("review.html", {"request": request})
    return HTMLResponse(content="<h1>Review interface coming soon...</h1>")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "RFP Analyzer Enhanced Web App"}


if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    Path("uploads").mkdir(exist_ok=True)
    Path("outputs/exports").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    print("=" * 70)
    print("RFP Analyzer - Enhanced Web Application")
    print("=" * 70)
    print()
    print("🚀 Starting server on http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")