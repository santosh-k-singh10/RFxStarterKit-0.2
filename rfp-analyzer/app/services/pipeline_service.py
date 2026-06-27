"""
app/services/pipeline_service.py
---------------------------------
Service layer for running the LangGraph pipeline.
"""

from typing import Callable, Optional, cast
import structlog
from pathlib import Path

from core.state import build_graph, cleanup_checkpoint_db
from core.schemas import AnalysisState, AnalysisStateDict
from langchain_core.runnables import RunnableConfig

log = structlog.get_logger(__name__)


async def run_pipeline(
    file_path: str,
    title: str,
    min_confidence: float = 0.0,
    thread_id: Optional[str] = None,
    progress_callback: Optional[Callable] = None
) -> AnalysisState:
    """
    Execute the LangGraph pipeline with progress tracking.
    
    Args:
        file_path: Path to uploaded RFP file
        title: Analysis title
        min_confidence: Minimum confidence threshold
        thread_id: Optional thread ID for checkpointing
        progress_callback: Optional callback for progress updates
    
    Returns:
        Final AnalysisState with all requirements
    """
    log.info("pipeline_start", file_path=file_path, title=title)
    
    # Generate thread ID if not provided
    if not thread_id:
        import uuid
        thread_id = str(uuid.uuid4())
    
    # Clean up old checkpoints for this thread
    checkpoint_db = "./logs/checkpoints.sqlite"
    Path("./logs").mkdir(parents=True, exist_ok=True)
    
    # Build graph
    graph = build_graph(checkpoint_db=checkpoint_db)
    
    # Create initial state
    initial_state_model = AnalysisState(
        file_path=file_path,
        metadata={"title": title}
    )
    initial_state = cast(AnalysisStateDict, initial_state_model.model_dump())
    
    # Config for LangGraph with thread_id for checkpointing
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    
    # Execute graph
    try:
        if progress_callback:
            await progress_callback("ingest", "running")
        
        final_state_dict = graph.invoke(initial_state, config)
        final_state = AnalysisState(**final_state_dict)
        
        # Filter by confidence
        if min_confidence > 0.0:
            final_state.final_requirements = [
                r for r in final_state.final_requirements 
                if r.confidence >= min_confidence
            ]
        
        log.info("pipeline_complete", 
                requirements_count=len(final_state.final_requirements),
                thread_id=thread_id)
        
        if progress_callback:
            await progress_callback("done", "completed")
        
        return final_state
        
    except Exception as e:
        log.error("pipeline_error", error=str(e), thread_id=thread_id)
        if progress_callback:
            await progress_callback("error", str(e))
        raise