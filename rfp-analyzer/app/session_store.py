"""
app/session_store.py
--------------------
Session management for the web application.

In-memory storage for development, with Redis support for production.
"""

import uuid
from typing import Dict, Optional
from datetime import datetime, timedelta
import structlog

from core.schemas import RFPContext, AnalysisState

log = structlog.get_logger(__name__)

# In-memory store (replace with Redis in production)
_store: Dict[str, RFPContext] = {}


def create_session(file_path: str, title: str, domain: Optional[str] = None) -> str:
    """
    Create a new session for an RFP analysis.
    
    Args:
        file_path: Path to the uploaded RFP file
        title: Analysis title
        domain: Optional domain/industry
    
    Returns:
        session_id: Unique session identifier
    """
    session_id = str(uuid.uuid4())
    
    ctx = RFPContext(
        session_id=session_id,
        file_path=file_path,
        title=title,
        domain=domain,
        state=AnalysisState(file_path=file_path),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    _store[session_id] = ctx
    log.info("session_created", session_id=session_id, title=title)
    
    return session_id


def get_session(session_id: str) -> Optional[RFPContext]:
    """
    Retrieve a session by ID.
    
    Args:
        session_id: Session identifier
    
    Returns:
        RFPContext or None if not found
    """
    ctx = _store.get(session_id)
    if ctx:
        log.debug("session_retrieved", session_id=session_id)
    else:
        log.warning("session_not_found", session_id=session_id)
    return ctx


def save_session(session_id: str, ctx: RFPContext) -> None:
    """
    Save/update a session.
    
    Args:
        session_id: Session identifier
        ctx: Updated RFPContext
    """
    ctx.updated_at = datetime.now()
    _store[session_id] = ctx
    log.debug("session_saved", session_id=session_id)


def delete_session(session_id: str) -> bool:
    """
    Delete a session.
    
    Args:
        session_id: Session identifier
    
    Returns:
        True if deleted, False if not found
    """
    if session_id in _store:
        del _store[session_id]
        log.info("session_deleted", session_id=session_id)
        return True
    return False


def list_sessions() -> list[dict]:
    """
    List all active sessions (metadata only).
    
    Returns:
        List of session metadata dicts
    """
    return [
        {
            "session_id": ctx.session_id,
            "title": ctx.title,
            "created_at": ctx.created_at.isoformat(),
            "updated_at": ctx.updated_at.isoformat(),
            "requirements_count": len(ctx.state.final_requirements)
        }
        for ctx in _store.values()
    ]


def cleanup_old_sessions(max_age_hours: int = 24) -> int:
    """
    Clean up sessions older than specified age.
    
    Args:
        max_age_hours: Maximum age in hours
    
    Returns:
        Number of sessions deleted
    """
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    to_delete = [
        sid for sid, ctx in _store.items()
        if ctx.updated_at < cutoff
    ]
    
    for sid in to_delete:
        del _store[sid]
    
    if to_delete:
        log.info("old_sessions_cleaned", count=len(to_delete))
    
    return len(to_delete)


# ─────────────────────────────────────────────────────────────────────────────
# Redis implementation (for production)
# ─────────────────────────────────────────────────────────────────────────────

# TODO: Uncomment and configure for production use
"""
import redis
import json

redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

SESSION_TTL = 14400  # 4 hours

def create_session_redis(file_path: str, title: str, domain: Optional[str] = None) -> str:
    session_id = str(uuid.uuid4())
    ctx = RFPContext(
        session_id=session_id,
        file_path=file_path,
        title=title,
        domain=domain,
        state=AnalysisState(file_path=file_path),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    redis_client.setex(
        f"session:{session_id}",
        SESSION_TTL,
        ctx.model_dump_json()
    )
    
    return session_id

def get_session_redis(session_id: str) -> Optional[RFPContext]:
    data = redis_client.get(f"session:{session_id}")
    if 
        return RFPContext.model_validate_json(data)
    return None

def save_session_redis(session_id: str, ctx: RFPContext) -> None:
    ctx.updated_at = datetime.now()
    redis_client.setex(
        f"session:{session_id}",
        SESSION_TTL,
        ctx.model_dump_json()
    )
"""