"""
app/routers/exports.py
----------------------
API endpoints for exporting requirements.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import FileResponse
import structlog

from app.session_store import get_session
from app.services.export_service import export_to_excel, export_to_markdown, export_to_json
from core.schemas import ReviewStatus

log = structlog.get_logger(__name__)

router = APIRouter(tags=["exports"])


@router.get("/api/export/excel")
async def export_excel(session_id: str = Cookie(None)):
    """Export requirements to Excel."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Filter to accepted/modified requirements
    reqs = [r for r in ctx.state.final_requirements 
            if r.review_status in [ReviewStatus.ACCEPTED, ReviewStatus.MODIFIED]]
    
    if not reqs:
        raise HTTPException(400, "No accepted requirements to export")
    
    # Export
    output_dir = Path("outputs") / "exports" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ctx.title.replace(' ', '_')}_requirements.xlsx"
    output_path = output_dir / filename
    
    await export_to_excel(reqs, str(output_path))
    
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )


@router.get("/api/export/markdown")
async def export_markdown(session_id: str = Cookie(None)):
    """Export requirements to Markdown."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Filter to accepted/modified requirements
    reqs = [r for r in ctx.state.final_requirements 
            if r.review_status in [ReviewStatus.ACCEPTED, ReviewStatus.MODIFIED]]
    
    if not reqs:
        raise HTTPException(400, "No accepted requirements to export")
    
    # Export
    output_dir = Path("outputs") / "exports" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ctx.title.replace(' ', '_')}_requirements.md"
    output_path = output_dir / filename
    
    await export_to_markdown(reqs, str(output_path), ctx.title)
    
    return FileResponse(
        output_path,
        media_type="text/markdown",
        filename=filename
    )


@router.get("/api/export/json")
async def export_json(session_id: str = Cookie(None)):
    """Export requirements to JSON."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Filter to accepted/modified requirements
    reqs = [r for r in ctx.state.final_requirements 
            if r.review_status in [ReviewStatus.ACCEPTED, ReviewStatus.MODIFIED]]
    
    if not reqs:
        raise HTTPException(400, "No accepted requirements to export")
    
    # Export
    output_dir = Path("outputs") / "exports" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ctx.title.replace(' ', '_')}_requirements.json"
    output_path = output_dir / filename
    
    await export_to_json(reqs, str(output_path), ctx.title)
    
    return FileResponse(
        output_path,
        media_type="application/json",
        filename=filename
    )


@router.get("/api/export/solution-map")
async def export_solution_map(session_id: str = Cookie(None)):
    """Export solution mapping to JSON."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    if not ctx.solution_map:
        raise HTTPException(400, "No solution mapping available")
    
    # Export solution map
    import json
    output_dir = Path("outputs") / "exports" / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{ctx.title.replace(' ', '_')}_solution_mapping.json"
    output_path = output_dir / filename
    
    with open(output_path, 'w') as f:
        json.dump(ctx.solution_map, f, indent=2)
    
    return FileResponse(
        output_path,
        media_type="application/json",
        filename=filename
    )