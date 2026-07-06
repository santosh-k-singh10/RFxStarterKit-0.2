# Architecture Documentation

## System Overview

RFxStarterKit is built as a modular, microservices-based architecture with three main components:

1. **RFP Analyzer** - Document analysis and requirement extraction
2. **Phase 0 Document Router** - Multi-document processing and classification
3. **Scoping Architect** - Solution architecture and scoping

---

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Frontend Layer                         │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │  Web Interface │  │   REST API     │  │   CLI Tools    │ │
│  │  (HTML/JS)     │  │  (FastAPI)     │  │   (Typer)      │ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Application Layer                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                  Phase 0 Router                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │Classifier│  │ Chunker  │  │ Conflict │  │Assembler│ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
│                              │                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   RFP Analyzer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │Functional│  │Compliance│  │Ambiguity │  │  Risk  │ │  │
│  │  │  Agent   │  │  Agent   │  │  Agent   │  │ Agent  │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
│                              │                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │               Scoping Architect                         │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │  │
│  │  │Component │  │Estimation│  │  Risk    │  │ Export │ │  │
│  │  │Identifier│  │  Engine  │  │Analyzer  │  │ Engine │ │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Integration Layer                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │   LLM APIs     │  │  File Storage  │
└──────────────────────────────────────────────────────────────┘
                              │
┌──────────────────────────────────────────────────────────────┐
│                      Integration Layer                        │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │   LLM APIs     │  │  File Storage  │  │   MCP Server   │ │
│  │ OpenAI/Claude  │  │  /uploads      │  │ (mcp_server.py)│ │
│  └────────────────┘  └────────────────┘  └────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## Phase 0 Data Flow (multi-document ingestion)

```
User uploads N documents
        │
        ▼
┌─────────────────────────────────────────────┐
│  Phase 0 Document Router                     │
│  document-consolidator/phase0_router/        │
│                                              │
│  1. Classifier  — tag each doc by type       │
│     (rfp | sow | compliance | pricing | …)   │
│                                              │
│  2. Chunker     — semantic section splits    │
│                                              │
│  3. Conflict Detector — cross-doc diff       │
│                                              │
│  4. Assembler   — unified DocumentContext    │
└────────────────────┬────────────────────────┘
                     │  DocumentContext (JSON)
                     ▼
┌─────────────────────────────────────────────┐
│  Phase 0 Adapter  (core/phase0_adapter.py)   │
│  Converts DocumentContext → chunks list      │
│  that the RFP Analyzer graph accepts         │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  RFP Analyzer Pipeline  (LangGraph graph)    │
│                                              │
│  Parallel agents (each chunk → all agents)   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │Functional│ │Compliance│ │Ambiguity │    │
│  └──────────┘ └──────────┘ └──────────┘    │
│  ┌──────────┐ ┌──────────┐                  │
│  │Non-Func  │ │  Risk    │                  │
│  └──────────┘ └──────────┘                  │
│                     │                        │
│             Synthesizer Agent                │
│  (dedup, cross-link, confidence scoring)     │
└────────────────────┬────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
   Markdown        Excel         HTML
   JSON            (xlsx)    (by category
                              or by module)
```

**Fallback:** when Phase 0 is unavailable (missing `ANTHROPIC_API_KEY` or install), `core/ingestor.py` handles single-document ingestion directly and the graph proceeds unchanged.

---

## Key Design Decisions

See [`docs/adr/`](adr/) for the full rationale behind each choice.

| ADR | Decision |
|-----|----------|
| [ADR-0001](adr/ADR-0001-llm-provider-selection.md) | OpenAI primary, Claude for Phase 0; `OPENAI_API_BASE` override for any compatible endpoint |
| [ADR-0002](adr/ADR-0002-multi-agent-langgraph.md) | LangGraph for orchestration + SQLite checkpointing |
| [ADR-0003](adr/ADR-0003-skills-vs-agents-evaluation.md) | Standalone pipeline exposed via MCP rather than pure watsonx Orchestrate Skills |

---

## Repository Structure

```
RFxStarterKit-0.1/
├── rfp-analyzer/
│   ├── web_app.py               ← production entry point (web UI)
│   ├── main.py                  ← CLI entry point
│   ├── agents/                  ← one file per requirement category
│   ├── core/                    ← graph, state, ingestor, schemas
│   ├── outputs/                 ← exporters (markdown, excel, json, html)
│   ├── org_context/             ← organisational context management
│   └── mcp_server.py            ← MCP tool wrapper for WxO integration
│
├── scoping-architect/
│   ├── app.py                   ← FastAPI app (port 8001)
│   ├── router.py                ← route handlers
│   └── scoping_designer/        ← architecture generation logic
│
├── document-consolidator/
│   └── phase0_router/           ← Phase 0 multi-document router
│       └── phase0/
│           ├── router.py
│           ├── classifier.py
│           ├── chunker.py
│           ├── conflict_detector.py
│           └── assembler.py
│
├── common/
│   └── .env                     ← shared environment configuration
│
└── docs/
    ├── ARCHITECTURE.md          ← this file
    ├── QUICK_START.md           ← setup and running instructions
    ├── API_REFERENCE.md         ← REST endpoint reference
    ├── DOCKER_GUIDE.md          ← Docker deployment
    └── adr/                     ← Architecture Decision Records
```
