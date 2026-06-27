# Phase 0 Integration Guide
## Connecting Phase 0 into the existing Phase 1–3 Pipeline

---

### 1. Directory placement

Place the `phase0/` folder alongside your existing FastAPI app:

```
rfp_analyzer/
├── phase0/               ← new
│   ├── __init__.py
│   ├── api.py
│   ├── assembler.py
│   ├── chunker.py
│   ├── classifier.py
│   ├── conflict_detector.py
│   ├── router.py
│   ├── schema.py
│   └── utils.py
├── phase1/               ← existing
├── phase2/               ← existing
├── phase3/               ← existing
└── main.py               ← existing FastAPI app
```

---

### 2. Mount Phase 0 into your existing FastAPI app

In `main.py`, include the Phase 0 router:

```python
from phase0.api import app as phase0_app
from fastapi import FastAPI

app = FastAPI()

# Mount Phase 0 as a sub-application
app.mount("/phase0", phase0_app)

# Or include the router directly:
# from phase0.api import app as phase0_router
# app.include_router(phase0_router.router)
```

Phase 0 will then be available at: `POST /phase0/analyze`

---

### 3. Phase 1 input change

**Before (single document):**
```python
@app.post("/analyze")
async def analyze(file: UploadFile):
    text = extract_text(file)
    requirements = extract_requirements(text)
    return requirements
```

**After (multi-document via Phase 0):**
```python
from phase0.schema import DocumentContext, PhaseTarget

@app.post("/analyze")
async def analyze(document_text: str, rfp_id: str, source_documents: list[str]):
    # document_text is now the assembled Phase 1 context from Phase 0
    # Each chunk is prefixed with [SOURCE: filename | page | section_type]
    requirements = extract_requirements(document_text)

    # Add source_document field to each extracted requirement
    for req in requirements:
        req["rfp_id"] = rfp_id
    return requirements
```

---

### 4. Adding source traceability to Phase 1 output

In your Phase 1 extraction prompt, add this instruction:

```
Each requirement you extract must include a "source_document" field.
Extract it from the [SOURCE: filename | page | section_type] prefix
that appears before each text block.

Example output:
{
  "req_id": "IBM-FR-001",
  "description": "...",
  "source_document": "tech_spec.pdf",
  "page_ref": "p.4",
  ...
}
```

This gives you end-to-end traceability: client asks "where did this come from?" → instant answer.

---

### 5. Phase 3 (PERT estimation) — use phase3 context

Phase 3 gets timeline and pricing chunks that Phase 1/2 don't see:

```python
# In your Phase 3 estimation logic, optionally consume Phase 0 output:
phase3_chunks = doc_context.get_phase_chunks(PhaseTarget.PHASE3)
timeline_text = "\n".join(c.content for c in phase3_chunks
                          if c.section_type.value in ["timeline", "pricing"])
```

---

### 6. Running Phase 0 standalone (for testing)

```python
from phase0.router import Phase0Router

router = Phase0Router()
doc_context = router.run([
    "path/to/tech_spec.pdf",
    "path/to/compliance.docx",
    "path/to/pricing.xlsx",
])

print(f"RFP ID: {doc_context.rfp_id}")
print(f"Conflicts: {len(doc_context.conflicts)}")
print(f"Phase 1 chunks: {len(doc_context.get_phase_chunks('phase1'))}")
```

---

### 7. Environment variables

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # required
export PHASE0_CONFIDENCE_THRESHOLD=0.70  # optional, default 0.70
export PHASE0_MAX_CHUNKS_PER_DOC=80      # optional, default 80
```

---

### 8. Running tests

```bash
cd phase0_router
pip install -r requirements.txt
pytest tests/ -v
```

Expected output: 14 tests, all passing (with mocked LLM calls — no API key needed for tests).
