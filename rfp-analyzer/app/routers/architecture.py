"""
app/routers/architecture.py
----------------------------
API endpoints for architecture diagram generation.
"""

from fastapi import APIRouter, HTTPException, Cookie
from pydantic import BaseModel
import structlog

from app.session_store import get_session, save_session
from app.services.claude_service import generate_architecture_diagram, identify_components

log = structlog.get_logger(__name__)

router = APIRouter(tags=["architecture"])


class ArchitectureRequest(BaseModel):
    pass  # Uses session_id from cookie


@router.post("/api/architecture/diagram")
async def create_diagram(
    session_id: str = Cookie(None)
):
    """Generate architecture diagram from requirements."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Check cache
    if ctx.architecture_diagram:
        return {"mermaid_code": ctx.architecture_diagram, "cached": True}
    
    # Generate diagram
    reqs_dict = [r.model_dump() for r in ctx.state.final_requirements]
    diagram = await generate_architecture_diagram(reqs_dict)
    
    # Cache result
    ctx.architecture_diagram = diagram
    save_session(session_id, ctx)
    
    log.info("architecture_diagram_generated", session_id=session_id)
    
    return {"mermaid_code": diagram, "cached": False}


@router.post("/api/architecture/components")
async def create_components(
    session_id: str = Cookie(None)
):
    """Identify system components from requirements."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Check cache
    if ctx.system_components:
        return {"components": ctx.system_components, "cached": True}
    
    # Identify components
    reqs_dict = [r.model_dump() for r in ctx.state.final_requirements]
    components = await identify_components(reqs_dict)
    
    # Cache result
    ctx.system_components = components
    save_session(session_id, ctx)
    
    log.info("components_identified", session_id=session_id, count=len(components))
    
    return {"components": components, "cached": False}