"""
app/routers/clarifications.py
------------------------------
API endpoints for handling clarification answers.
"""

from fastapi import APIRouter, HTTPException, Cookie
from pydantic import BaseModel
import structlog

from app.session_store import get_session, save_session

log = structlog.get_logger(__name__)

router = APIRouter(tags=["clarifications"])


class ClarificationAnswer(BaseModel):
    answer: str
    answer_source: str


@router.post("/api/clarifications/{req_id}/answer")
async def submit_answer(
    req_id: str,
    answer: ClarificationAnswer,
    session_id: str = Cookie(None)
):
    """Submit answer to a clarification question."""
    if not session_id:
        raise HTTPException(401, "No session found")
    
    ctx = get_session(session_id)
    if not ctx:
        raise HTTPException(404, "Session not found")
    
    req = next((r for r in ctx.state.final_requirements if r.id == req_id), None)
    if not req:
        raise HTTPException(404, f"Requirement {req_id} not found")
    
    # Update requirement with answer
    req.clarification_answer = answer.answer
    req.answer_source = answer.answer_source
    req.ambiguity_flag = False
    req.reanalysis_triggered = True
    
    save_session(session_id, ctx)
    
    log.info("clarification_answered", req_id=req_id, source=answer.answer_source)
    
    return {
        "req_id": req_id,
        "reanalysis_triggered": True,
        "updated_requirement": req.model_dump()
    }