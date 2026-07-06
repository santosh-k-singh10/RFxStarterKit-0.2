# ADR-0003: watsonx Orchestrate Skills vs. Custom Agents

**Status:** Accepted  
**Date:** 2026-07-03  
**Deciders:** Core team

---

## Context

IBM watsonx Orchestrate (WxO) exposes an **Agentic Skills** API that packages LLM tasks as reusable, governed, discoverable units deployable into the WxO catalog. The question was whether to build the RFP analysis pipeline as a set of WxO Skills, or as a standalone multi-agent system (see ADR-0002) exposed to WxO as a single MCP-compatible tool.

---

## Decision

Build as a **standalone multi-agent system** (LangGraph) and expose it to WxO via an **MCP server** (`rfp-analyzer/mcp_server.py`). WxO Skills are used as the integration boundary — a thin wrapper that calls the MCP tool — rather than as the implementation layer.

---

## Evaluation Summary

| Criterion | WxO Skills as implementation | Standalone + MCP wrapper |
|-----------|------------------------------|--------------------------|
| Development speed | Slower (WxO schema/catalog overhead per agent) | Faster (standard Python) |
| Testability | Limited (requires WxO sandbox) | Full unit + integration tests |
| Portability | WxO-only | Runs standalone or via any MCP-compatible host |
| Governance / auditability | Strong (WxO catalog, RBAC) | Must implement separately |
| Parallel agent execution | Constrained by Skills API | Full control via LangGraph |
| Checkpoint / resume | Not available in Skills | Native LangGraph SQLite |

---

## Why not pure WxO Skills

- The five extraction agents share intermediate state (chunks, partial results). The Skills API is stateless per invocation; passing state between five sequential skill calls would require external storage and significantly more complexity.
- Checkpointing (resume interrupted run) is a first-class requirement; it has no equivalent in the Skills model.
- Local development and testing without a WxO tenant would be blocked.

---

## Consequences

- `rfp-analyzer/mcp_server.py` provides the `analyze_rfp`, `get_analysis_status`, `get_analysis_results`, and `list_analyses` MCP tools that WxO or any MCP-compatible AI gateway can call.
- WxO deployment is additive — the system is fully usable without WxO.
- If WxO governance requirements increase, individual agents can be promoted to Skills independently without rewriting the core pipeline.
