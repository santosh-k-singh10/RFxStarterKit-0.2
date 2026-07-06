# Architecture Decision Records

This directory captures the *why* behind significant design choices in RFxStarterKit.
Each ADR is numbered, immutable once accepted, and superseded by a new ADR if the decision changes.

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](ADR-0001-llm-provider-selection.md) | LLM Provider Selection | Accepted |
| [ADR-0002](ADR-0002-multi-agent-langgraph.md) | Multi-Agent Orchestration with LangGraph | Accepted |
| [ADR-0003](ADR-0003-skills-vs-agents-evaluation.md) | watsonx Orchestrate Skills vs. Custom Agents | Accepted |

## Format

Each ADR follows the structure: **Context → Decision → Alternatives Considered → Consequences**.

To propose a new ADR, copy one of the existing files, increment the number, set Status to `Proposed`, and open a PR.
