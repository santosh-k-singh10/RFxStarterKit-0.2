# ADR-0002: Multi-Agent Orchestration with LangGraph

**Status:** Accepted  
**Date:** 2026-07-03  
**Deciders:** Core team

---

## Context

RFP analysis requires extracting five distinct requirement types (functional, non-functional, compliance, ambiguity, risk) from the same document. Each type benefits from a specialist prompt and can be parallelised. We needed an orchestration layer that:

1. Runs agents in parallel where possible
2. Maintains shared state across agents
3. Supports resumable runs (checkpoint / restart after failure)
4. Produces deterministic, testable output

---

## Decision

Use **LangGraph** as the orchestration layer with:

- One specialised `BaseAgent` subclass per requirement category (5 agents total)
- A `Synthesizer` agent that deduplicates and cross-links outputs
- SQLite-backed checkpointing (`langgraph.checkpoint.sqlite`) so interrupted runs can be resumed with the same `thread_id`
- Shared state via a typed `AnalysisState` / `AnalysisStateDict` Pydantic model

---

## Alternatives Considered

| Option | Reason rejected |
|--------|----------------|
| Single monolithic prompt | Too large; hallucination rate increased with all five tasks in one prompt |
| CrewAI | Less control over state shape and checkpoint semantics at evaluation time |
| Celery task queue | Overkill for a single-user local tool; adds Redis/RabbitMQ dependency |
| Plain `asyncio.gather` | No built-in state management or checkpointing |

---

## Consequences

- Adding a new requirement category = add one `BaseAgent` subclass and wire it into `core/state.py`. No orchestration refactoring needed.
- The `thread_id` / `--thread-id` CLI option exposes checkpointing to end users, enabling retry without re-running the full pipeline.
- LangGraph pins the `langchain-core` version; upgrading requires testing the full graph.
