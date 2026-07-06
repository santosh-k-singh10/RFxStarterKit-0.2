# Quick Start Guide

Get RFxStarterKit running in under 5 minutes.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3.9+ | |
| `OPENAI_API_KEY` | Required for RFP analysis |
| `ANTHROPIC_API_KEY` | Optional — enables Phase 0 multi-document processing |
| Docker + Docker Compose | Optional — for containerised deployment |

---

## Option 1 — Docker (recommended for production)

```bash
git clone https://github.com/santosh-k-singh10/RFxStarterKit-0.1.git
cd RFxStarterKit-0.1

cp .env.example .env          # then edit .env with your API keys

docker-compose up --build
```

Services available at:
- **RFP Analyzer** → http://localhost:8080
- **Scoping Architect** → http://localhost:8001

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for compose options, volume mounts, and resource limits.

---

## Option 2 — Local Python

### 1. Install dependencies

Each service is a proper Python package. Install them in editable mode so
imports resolve without any `sys.path` hacks:

```bash
# Install service packages as editable (one-time, from repo root)
pip install -e ./rfp-analyzer
pip install -e ./document-consolidator/phase0_router   # optional: Phase 0
pip install -e ./scoping-architect                     # optional: Scoping

# Install shared tooling + dev deps
pip install -r requirements.txt
```

> **Why `-e`?** It registers the packages (`agents`, `core`, `phase0`, etc.)
> into your Python environment so every script and test can import them by
> name, without `sys.path` manipulation. See the service-level
> `pyproject.toml` in each directory for details.

### 2. Configure environment

```bash
cp .env.example .env
# Set at minimum:
#   OPENAI_API_KEY=sk-...
#   ANTHROPIC_API_KEY=sk-ant-...   (optional, for Phase 0)
```

The `.env` at the repo root is shared by all services. Per-service overrides go in `rfp-analyzer/.env` or `scoping-architect/.env`.

### 3. Start RFP Analyzer

```bash
cd rfp-analyzer
uvicorn web_app:app --reload --port 8080
```

Open http://localhost:8080 → upload an RFP → review results.

### 4. Start Scoping Architect (optional)

In a second terminal:

```bash
cd scoping-architect
uvicorn app:create_app --factory --reload --port 8001
```

Open http://localhost:8001 → load RFP analysis JSON → generate architecture scope.

---

## Running both services together

| Terminal | Command |
|----------|---------|
| 1 | `cd rfp-analyzer && uvicorn web_app:app --reload --port 8080` |
| 2 | `cd scoping-architect && uvicorn app:create_app --factory --reload --port 8001` |

With both running, the **🏗️ Scoping Questionnaire** and **🔍 Generate Scope** tabs inside the RFP Analyzer UI connect to the Scoping Architect automatically.

### Integration endpoints (RFP Analyzer → Scoping Architect)

```
GET  /api/scoping/health          check scoping-architect availability
POST /api/scoping/analyze         generate architecture scope
POST /api/scoping/preferences     validate preferences
GET  /api/scoping/bridge/{job_id} get bridge data
```

---

## CLI usage (batch / scripted runs)

```bash
cd rfp-analyzer
python main.py analyze path/to/rfp.pdf
python main.py analyze path/to/rfp.pdf --output-dir ./results --title "Project Alpha"
python main.py analyze path/to/rfp.pdf --no-excel --no-markdown
python main.py analyze path/to/rfp.pdf --thread-id my-run-1   # resume interrupted run
```

---

## Startup sequence (what to expect)

```
INFO  Loading environment from .env
INFO  Phase 0 available: True
INFO  Preloading sentence-transformer model...     ← takes 30–60 s on first start
INFO  Models preloaded successfully
INFO  Uvicorn running on http://0.0.0.0:8080
```

First startup is slow due to model download. Subsequent starts use the cache.

---

## Performance expectations

| Metric | Typical value |
|--------|--------------|
| Startup (cold) | 30–60 s |
| File upload | < 1 s |
| Single-doc analysis (10 pages) | 1–2 min |
| Single-doc analysis (100 pages) | 5–8 min |
| Memory | ~500 MB with model loaded |

---

## Troubleshooting

### `ModuleNotFoundError` on start

```bash
pip install -r requirements.txt
```

### `Could not resolve authentication method`

Verify `OPENAI_API_KEY` (and optionally `OPENAI_API_BASE`) are set in `.env`.

### Phase 0 not available

Install Phase 0 dependencies and set `ANTHROPIC_API_KEY`. The system falls back gracefully to single-document mode without Phase 0.

### Port already in use

```bash
uvicorn web_app:app --reload --port 8081   # pick any free port
```

### CORS errors between services

Both services default to `allow_origins=["*"]`. If errors persist, confirm both are running on the expected ports and check browser console for the specific blocked URL.
