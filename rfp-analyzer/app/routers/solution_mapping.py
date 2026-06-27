"""
app/routers/solution_mapping.py
--------------------------------
API endpoints for solution mapping.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Cookie
from pydantic import BaseModel
import structlog

from app.session_store import get_session, save_session
from app.services.claude_service import map_to_solutions

log = structlog.get_logger(__name__)

router = APIRouter(tags=["solution_mapping"])


class SolutionMappingRequest(BaseModel):
    solutions: List[str]


@router.post("/api/solution-mapping")
async def create_solution_mapping(
    request: SolutionMappingRequest,
    session_id: str = Cookie(None)
):
    """Map requirements to target solutions."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    # Check cache
    if ctx.solution_map:
        return {**ctx.solution_map, "cached": True}
    
    # Generate solution mapping
    reqs_dict = [r.model_dump() for r in ctx.state.final_requirements]
    result = await map_to_solutions(reqs_dict, request.solutions)
    
    # Update requirements with mapping
    mapping_dict = {item["req_id"]: item for item in result["mapping"]}
    for req in ctx.state.final_requirements:
        if req.id in mapping_dict:
            item = mapping_dict[req.id]
            req.best_fit_solution = item.get("best_fit_solution")
            req.solution_coverage = item.get("coverage")
            req.solution_module = item.get("module")
            req.solution_rationale = item.get("rationale")
    
    # Cache result
    ctx.solution_map = result
    save_session(session_id, ctx)
    
    log.info("solution_mapping_complete", session_id=session_id, 
            solutions=len(request.solutions))
    
    return {**result, "cached": False}