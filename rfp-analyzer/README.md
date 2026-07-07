# RFP Analyzer

Multi-agent RFP analysis service. Extracts and categorises requirements from proposal documents using a LangGraph pipeline backed by Claude via IBM Services Essentials.

---

## Entry Points

| File | Purpose | How to run |
|------|---------|------------|
| **`web_app.py`** | ✅ Production web UI | `uvicorn web_app:app --reload --port 8080` |
| `main.py` | CLI — batch/scripted runs | `python main.py analyze rfp.pdf` |
| `mcp_server.py` | MCP tool server for WxO integration | `python mcp_server.py` |

---

## Quick Start

```bash
# From repo root — install dependencies
pip install -r requirements.txt

# Configure environment (once)
cp common/.env.template common/.env
# Edit common/.env — set OPENAI_API_KEY to your IBM Services Essentials token

# Start the web interface
cd rfp-analyzer
uvicorn web_app:app --reload --port 8080
```

Open http://localhost:8080, upload an RFP, review results.

---

## Agents

| Agent | File | Extracts |
|-------|------|---------|
| Functional | `agents/functional.py` | Features, workflows, integrations |
| Non-Functional | `agents/nonfunctional.py` | SLAs, performance, security |
| Compliance | `agents/compliance.py` | Regulatory obligations, certifications |
| Ambiguity | `agents/ambiguity.py` | Vague language, clarification questions |
| Risk | `agents/risk.py` | Complexity, timeline, dependency risks |
| Synthesizer | `agents/synthesizer.py` | Deduplication, cross-linking, sorting |

Each agent is a single Python file with a module-level `SYSTEM_PROMPT` constant and a single public `extract_*()` function.

---

## Pipeline

```
Documents
   │
   ├─ (multiple files) → Phase 0 Router → unified chunks
   └─ (single file)   → core/ingestor.py → chunks
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
              Functional   Compliance   Non-Func  …  (parallel)
                    └───────────┼───────────┘
                                ▼
                          Synthesizer
                          (dedup + cross-link + sort)
                                │
                   ┌────────────┼────────────┐
                   ▼            ▼            ▼
                Excel         JSON         HTML
```

---

## CLI Usage

```bash
python main.py analyze path/to/rfp.pdf
python main.py analyze path/to/rfp.pdf --output-dir ./results --title "Project Alpha"
python main.py analyze path/to/rfp.pdf --min-confidence 0.7
python main.py analyze path/to/rfp.pdf --thread-id my-run-1   # resume interrupted run
```

---

## Configuration

All environment variables are read from `common/.env` at the repo root.
See [`common/.env.template`](../common/.env.template) for the full reference.

Key variables:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | IBM Services Essentials token (required) |
| `OPENAI_API_BASE` | `https://servicesessentials.ibm.com/apis/v3` |
| `MODEL_ID` | `global/anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `ANTHROPIC_API_KEY` | Optional — direct Anthropic calls for Phase 0 |
| `CONTEXT_STUDIO_ENABLED` | Enable Context Studio org-context integration |
| `OBSERVABILITY_ENABLED` | Enable Arize Phoenix tracing |

---

## Output Formats

| Format | Description |
|--------|-------------|
| Excel (`.xlsx`) | Filterable, grouped by category |
| JSON | Machine-readable, full metadata |
| Markdown | Human-readable report |
| HTML (by category) | Interactive viewer, collapsible sections |
| HTML (by module) | Grouped by SAP/system module |

---

## Project Structure

```
rfp-analyzer/
├── web_app.py          ← FastAPI web UI (production entry point)
├── main.py             ← CLI entry point
├── mcp_server.py       ← MCP tool server
├── agents/             ← one file per requirement category
│   ├── base.py         ← shared call_claude() + OpenAI client
│   ├── functional.py
│   ├── nonfunctional.py
│   ├── compliance.py
│   ├── ambiguity.py
│   ├── risk.py
│   └── synthesizer.py
├── core/
│   ├── ingestor.py     ← document → chunks
│   ├── embedder.py     ← FAISS RAG grounding verification
│   ├── schemas.py      ← Pydantic models
│   ├── state.py        ← LangGraph nodes + graph definition
│   └── phase0_adapter.py ← Phase 0 → analyzer bridge
├── outputs/            ← exporters (markdown, excel, json, html)
├── org_context/        ← organisational context management
└── observability/      ← Arize Phoenix tracing
```
