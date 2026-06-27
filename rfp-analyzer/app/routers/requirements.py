"""
app/routers/requirements.py
----------------------------
API endpoints for CRUD operations on requirements.
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Cookie, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import structlog

from app.session_store import get_session, save_session
from app.services.export_service import generate_html_preview
from core.schemas import Category, Priority, ReviewStatus

log = structlog.get_logger(__name__)

router = APIRouter(tags=["requirements"])


class RequirementUpdate(BaseModel):
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    confidence: Optional[float] = None
    review_status: Optional[ReviewStatus] = None
    reviewer_notes: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class BulkUpdate(BaseModel):
    req_ids: List[str]
    review_status: ReviewStatus


@router.get("/api/requirements")
async def get_requirements(
    session_id: Optional[str] = Cookie(None),
    session_query: Optional[str] = Query(None, alias="session_id"),
    category: Optional[str] = None,
    priority: Optional[str] = None,
    review_status: Optional[str] = None,
    min_confidence: Optional[float] = None,
    search: Optional[str] = None
):
    """Get filtered requirements."""
    resolved_session_id = session_id or session_query

    if not resolved_session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(resolved_session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    reqs = ctx.state.final_requirements
    
    # Apply filters
    if category:
        cats = [c.strip() for c in category.split(",")]
        reqs = [r for r in reqs if r.category.value in cats]
    
    if priority:
        pris = [p.strip() for p in priority.split(",")]
        reqs = [r for r in reqs if r.priority.value in pris]
    
    if review_status:
        statuses = [s.strip() for s in review_status.split(",")]
        reqs = [r for r in reqs if r.review_status.value in statuses]
    
    if min_confidence is not None:
        reqs = [r for r in reqs if r.confidence >= min_confidence]
    
    if search:
        search_lower = search.lower()
        reqs = [r for r in reqs if 
                search_lower in r.title.lower() or 
                search_lower in r.description.lower()]
    
    return {
        "requirements": [r.model_dump() for r in reqs],
        "total": len(ctx.state.final_requirements),
        "filtered": len(reqs)
    }


@router.get("/api/requirements/html-preview", response_class=HTMLResponse)
async def get_html_preview(
    session_id: Optional[str] = Cookie(None),
    session_query: Optional[str] = Query(None, alias="session_id")
):
    """
    Generate and return HTML preview of requirements categorized view.
    This returns the content that would be in RFP_Analysis_by_category.html
    """
    resolved_session_id = session_id or session_query

    if not resolved_session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(resolved_session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    if not ctx.state.final_requirements:
        raise HTTPException(404, "No requirements found in session")
    
    try:
        # Get RFP title from context or use default
        rfp_title = getattr(ctx.state, 'rfp_title', 'RFP Analysis')
        
        # Generate HTML preview
        html_content = await generate_html_preview(
            ctx.state.final_requirements,
            title=rfp_title
        )
        
        log.info("html_preview_generated", session_id=resolved_session_id,
                 req_count=len(ctx.state.final_requirements))
        
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        log.error("html_preview_error", error=str(e))
        raise HTTPException(500, f"Failed to generate HTML preview: {str(e)}")


@router.patch("/api/requirements/{req_id}")
async def update_requirement(
    req_id: str,
    update: RequirementUpdate,
    session_id: str = Cookie(None)
):
    """Update a single requirement."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Find requirement
    req = next((r for r in ctx.state.final_requirements if r.id == req_id), None)
    if not req:
        raise HTTPException(404, f"Requirement {req_id} not found")
    
    # Apply updates
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(req, field, value)
    
    # Mark as modified if review_status wasn't explicitly set
    if 'review_status' not in update_data:
        req.review_status = ReviewStatus.MODIFIED
    
    save_session(session_id, ctx)
    
    log.info("requirement_updated", req_id=req_id, fields=list(update_data.keys()))
    
    return {"req_id": req_id, "updated": True, "requirement": req.model_dump()}


@router.post("/api/requirements/bulk")
async def bulk_update(
    update: BulkUpdate,
    session_id: str = Cookie(None)
):
    """Bulk update requirements."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    updated_count = 0
    for req in ctx.state.final_requirements:
        if req.id in update.req_ids:
            req.review_status = update.review_status
            updated_count += 1
    
    save_session(session_id, ctx)
    
    log.info("bulk_update_complete", count=updated_count)
    
    return {"updated_count": updated_count}


@router.delete("/api/requirements/{req_id}")
async def delete_requirement(
    req_id: str,
    session_id: str = Cookie(None)
):
    """Soft delete a requirement."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    req = next((r for r in ctx.state.final_requirements if r.id == req_id), None)
    if not req:
        raise HTTPException(404, f"Requirement {req_id} not found")
    
    req.review_status = ReviewStatus.REJECTED
    save_session(session_id, ctx)
    
    log.info("requirement_deleted", req_id=req_id)
    
    return {"req_id": req_id, "dropped": True}