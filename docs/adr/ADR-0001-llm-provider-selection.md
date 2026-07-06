# ADR-0001: LLM Provider Selection

**Status:** Accepted  
**Date:** 2026-07-03  
**Deciders:** Core team

---

## Context

The system needs an LLM to power requirement extraction, ambiguity detection, risk assessment, and compliance classification. Multiple providers were available: OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), IBM watsonx, and open-source models via Ollama.

Key constraints:
- Structured JSON output required for reliable downstream parsing
- Long-context support needed for large RFP documents (50–200 pages)
- Must be callable from a Python backend without heavy infrastructure

---

## Decision

**Primary:** OpenAI GPT-4 class models via the `langchain-openai` adapter, configured through a `OPENAI_API_KEY` / `OPENAI_API_BASE` pair so the same code works against OpenAI, Azure OpenAI, or IBM-hosted OpenAI-compatible endpoints.

**Secondary (Phase 0):** Anthropic Claude 3.5 Sonnet for multi-document classification and conflict detection, where its extended context window (200k tokens) is a material advantage over GPT-4o's 128k.

---

## Alternatives Considered

| Option | Reason rejected |
|--------|----------------|
| IBM watsonx (Granite) | Structured JSON output was unreliable at the time of evaluation; no `tool_calls` API |
| Ollama / local models | Insufficient quality on long-context structured extraction without fine-tuning |
| Single provider (OpenAI only) | Phase 0 multi-document classification benefits materially from Claude's larger context |

---

## Consequences

- The `OPENAI_API_BASE` override means operators can point the system at any OpenAI-compatible endpoint (Azure, IBM, Anyscale) without code changes.
- `ANTHROPIC_API_KEY` is optional; Phase 0 falls back to standard single-document ingestion when absent.
- LLM switching is isolated to `rfp-analyzer/core/state.py` and `document-consolidator/phase0_router/phase0/llm_client.py`.
