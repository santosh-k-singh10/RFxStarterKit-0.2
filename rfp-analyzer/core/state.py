"""
core/state.py
-------------
LangGraph graph definition.

Graph topology
--------------
                    ┌─────────┐
                    │  ingest │
                    └────┬────┘
          ┌──────────────┼──────────────┐
     ┌────▼────┐   ┌─────▼──────┐  ┌───▼──────┐  ...
     │functional│  │nonfunctional│  │compliance│
     └────┬────┘   └─────┬──────┘  └───┬──────┘
          └──────────────┼──────────────┘
                    ┌────▼────┐
                    │synthesize│
                    └────┬────┘
                       (END)

All extraction agents run in parallel after ingestion.
The synthesizer waits for all of them via fan-in edges.

Checkpointing
-------------
Uses SqliteSaver so runs can be resumed if interrupted.
Pass the same thread_id to graph.invoke() to resume.
"""

from __future__ import annotations

import os
import structlog
from pathlib import Path
from langgraph.graph import StateGraph, END

from core.schemas import AnalysisState, AnalysisStateDict, DocumentChunk
from core.ingestor import ingest_document
from core.embedder import DocumentIndex
from agents.functional    import extract_functional
from agents.nonfunctional import extract_nonfunctional
from agents.compliance    import extract_compliance
from agents.ambiguity     import extract_ambiguities
from agents.risk          import extract_risks
from agents.synthesizer   import synthesize

log = structlog.get_logger()


# ─────────────────────────────────────────────────────────────────────────────
# Checkpoint cleanup utilities
# ─────────────────────────────────────────────────────────────────────────────

def cleanup_checkpoint_db(checkpoint_db: str = "./logs/checkpoints.sqlite") -> bool:
    """
    Delete the entire checkpoint database to start fresh.
    
    This prevents old RFP data from contaminating new analyses.
    Call this before starting a new analysis if you want a completely clean slate.
    
    Parameters
    ----------
    checkpoint_db : str
        Path to the SQLite checkpoint file
        
    Returns
    -------
    bool
        True if database was deleted, False if it didn't exist
    """
    db_path = Path(checkpoint_db)
    if db_path.exists():
        try:
            db_path.unlink()
            log.info("checkpoint_db_cleaned", path=str(db_path))
            return True
        except Exception as e:
            log.warning("checkpoint_db_cleanup_failed", path=str(db_path), error=str(e))
            return False
    return False


def cleanup_thread_checkpoints(checkpoint_db: str, thread_id: str) -> bool:
    """
    Clean up checkpoints for a specific thread_id.
    
    More surgical approach - only removes data for the specified thread.
    
    Parameters
    ----------
    checkpoint_db : str
        Path to the SQLite checkpoint file
    thread_id : str
        The thread ID to clean up
        
    Returns
    -------
    bool
        True if cleanup succeeded
    """
    db_path = Path(checkpoint_db)
    if not db_path.exists():
        return True
        
    try:
        import sqlite3
        conn = sqlite3.connect(checkpoint_db)
        cursor = conn.cursor()
        
        # Delete checkpoints for this thread_id
        cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        log.info("thread_checkpoints_cleaned", thread_id=thread_id, deleted=deleted_count)
        return True
    except Exception as e:
        log.warning("thread_checkpoint_cleanup_failed", thread_id=thread_id, error=str(e))
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Node functions
# Each node receives the full AnalysisState, mutates it, and returns it.
# ─────────────────────────────────────────────────────────────────────────────

def node_ingest(state: AnalysisStateDict) -> dict:
    """Parse the document and populate chunks."""
    s = AnalysisState(**state)
    log.info("node_ingest_start", file=s.file_path)

    result: dict = {
        "chunks": [],
        "document_text": "",
        "functional": [],
        "non_functional": [],
        "compliance": [],
        "ambiguities": [],
        "risks": [],
        "final_requirements": [],
        "errors": []
    }
    
    try:
        raw_chunks = ingest_document(s.file_path)
        result["chunks"] = raw_chunks
        result["document_text"] = "\n\n".join(chunk.text for chunk in raw_chunks)
        log.info("node_ingest_done", chunks=len(raw_chunks))
    except Exception as exc:  # noqa: BLE001
        result["errors"] = [f"Ingestion failed: {exc}"]
        result["chunks"] = []
        result["document_text"] = ""
        log.error("node_ingest_error", error=str(exc))

    return result


def node_functional(state: AnalysisStateDict) -> dict:
    s = AnalysisState(**state)
    log.info("node_functional_start")
    
    # Get organizational context
    org_context = _get_org_context()
    
    functional_reqs = extract_functional(s.chunks, org_context=org_context)
    log.info("functional_extraction_done", count=len(functional_reqs))
    return {"functional": functional_reqs}


def node_nonfunctional(state: AnalysisStateDict) -> dict:
    s = AnalysisState(**state)
    log.info("node_nonfunctional_start")
    
    # Get organizational context
    org_context = _get_org_context()
    
    nfr_reqs = extract_nonfunctional(s.chunks, org_context=org_context)
    log.info("nfr_extraction_done", count=len(nfr_reqs))
    return {"non_functional": nfr_reqs}


def node_compliance(state: AnalysisStateDict) -> dict:
    s = AnalysisState(**state)
    log.info("node_compliance_start")
    
    # Get organizational context
    org_context = _get_org_context()
    
    compliance_reqs = extract_compliance(s.chunks, org_context=org_context)
    log.info("compliance_extraction_done", count=len(compliance_reqs))
    return {"compliance": compliance_reqs}


def node_ambiguity(state: AnalysisStateDict) -> dict:
    s = AnalysisState(**state)
    log.info("node_ambiguity_start")
    
    # Get organizational context
    org_context = _get_org_context()
    
    ambiguity_reqs = extract_ambiguities(s.chunks, org_context=org_context)
    log.info("ambiguity_extraction_done", count=len(ambiguity_reqs))
    return {"ambiguities": ambiguity_reqs}


def node_risk(state: AnalysisStateDict) -> dict:
    s = AnalysisState(**state)
    log.info("node_risk_start")
    
    # Get organizational context
    org_context = _get_org_context()
    
    risk_reqs = extract_risks(s.chunks, org_context=org_context)
    log.info("risk_extraction_done", count=len(risk_reqs))
    return {"risks": risk_reqs}


def node_synthesize(state: AnalysisStateDict) -> dict:
    s = AnalysisState(**state)
    log.info("node_synthesize_start", raw_total=len(s.all_raw_requirements()))

    # Build RAG index for grounding verification
    doc_index = DocumentIndex(s.chunks) if s.chunks else None
    
    # Get organizational context for synthesis
    org_context = _get_org_context()

    final_reqs = synthesize(
        s.all_raw_requirements(),
        document_index=doc_index,
        org_context=org_context,
    )

    log.info("node_synthesize_done", final=len(final_reqs))
    return {"final_requirements": final_reqs}


def _get_org_context():
    """
    Helper function to get organizational context from the context manager.
    
    Returns None if context manager is not initialized or context is not available.
    This allows the system to work with or without organizational context.
    """
    try:
        from org_context import get_context_manager
        context_mgr = get_context_manager()
        if context_mgr:
            org_context = context_mgr.get_context()
            if org_context:
                log.debug("org_context_loaded", org_name=org_context.name)
                return org_context
        log.debug("org_context_not_available")
        return None
    except ImportError:
        log.debug("org_context_module_not_available")
        return None
    except Exception as e:
        log.warning("org_context_load_error", error=str(e))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Graph builder
# ─────────────────────────────────────────────────────────────────────────────

def build_graph(checkpoint_db: str = "./logs/checkpoints.sqlite"):
    """
    Construct and compile the LangGraph StateGraph.

    Parameters
    ----------
    checkpoint_db : str
        Path to the SQLite file used for run checkpointing.

    Returns
    -------
    CompiledGraph
        Ready-to-invoke graph.
    """
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        import sqlite3
        # Use timeout to prevent hanging on locked database
        conn = sqlite3.connect(checkpoint_db, check_same_thread=False, timeout=30.0)
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        memory = SqliteSaver(conn)
    except (ImportError, Exception) as e:
        from langgraph.checkpoint.memory import MemorySaver
        memory = MemorySaver()
        log.warning("sqlite_checkpointer_unavailable_using_memory", error=str(e))

    builder = StateGraph(AnalysisStateDict)   # Use AnalysisStateDict with Annotated reducers for concurrent updates

    # Register nodes
    builder.add_node("ingest",         node_ingest)
    builder.add_node("functional",     node_functional)
    builder.add_node("nonfunctional",  node_nonfunctional)
    builder.add_node("compliance",     node_compliance)
    builder.add_node("ambiguity",      node_ambiguity)
    builder.add_node("risk",           node_risk)
    builder.add_node("synthesize",     node_synthesize)

    # Entry
    builder.set_entry_point("ingest")

    # Fan-out: ingest → all extraction agents (parallel execution)
    for agent in ("functional", "nonfunctional", "compliance", "ambiguity", "risk"):
        builder.add_edge("ingest", agent)

    # Fan-in: all extraction agents → synthesize
    for agent in ("functional", "nonfunctional", "compliance", "ambiguity", "risk"):
        builder.add_edge(agent, "synthesize")

    # Terminal
    builder.add_edge("synthesize", END)

    return builder.compile(checkpointer=memory)
