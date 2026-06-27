# Phase 0 — Document Router Agent

Pre-processing layer for the RFP Analyzer Multi-Agent System.  
Sits upstream of Phase 1 (requirement extraction) and routes multi-document RFP packs into structured `document_context` objects consumed by each downstream phase.

---

## Architecture

```
[Multiple docs] → Classifier → Chunker → Conflict Detector → Context Assembler → document_context.json
```

| Sub-agent | Module | Responsibility |
|---|---|---|
| Classifier | `phase0/classifier.py` | Detects doc type + confidence score |
| Chunker | `phase0/chunker.py` | Section extraction + phase_relevance tagging |
| Conflict Detector | `phase0/conflict_detector.py` | Cross-doc contradiction detection |
| Context Assembler | `phase0/assembler.py` | Builds per-phase context windows |
| Router (orchestrator) | `phase0/router.py` | Orchestrates all sub-agents |
| FastAPI endpoint | `phase0/api.py` | `/phase0/analyze` — accepts multi-file upload |
| Schema | `phase0/schema.py` | Pydantic models for all I/O |

---

## document_context output schema

```json
{
  "rfp_id": "RFP-2024-001",
  "documents": [
    { "filename": "tech_spec.pdf", "doc_type": "technical_spec", "confidence": 0.94, "pages": 12 }
  ],
  "phase_contexts": {
    "phase1": [ ...chunks ],
    "phase2": [ ...chunks ],
    "phase3": [ ...chunks ]
  },
  "conflicts": [
    { "conflict_id": "C001", "chunk_ids": ["ch_003", "ch_041"], "description": "..." }
  ],
  "metadata": {
    "total_docs": 4,
    "total_chunks": 87,
    "conflict_count": 2
  }
}
```

---

## Chunk schema (every chunk carries)

```json
{
  "chunk_id": "ch_001",
  "source_document": "tech_spec.pdf",
  "page_ref": "p.4-5",
  "doc_type": "technical_spec",
  "section_type": "functional_requirement",
  "phase_relevance": ["phase1", "phase2"],
  "conflict_flag": false,
  "conflict_ref": null,
  "content": "..."
}
```

---

## Setup

```bash
pip install -r requirements.txt
uvicorn phase0.api:app --reload --port 8001
```

POST to `http://localhost:8001/phase0/analyze` with `multipart/form-data`, files under key `documents`.

---

## Session build log

| Part | Status | Description |
|---|---|---|
| Part 1 | ✅ Done | schema.py, classifier.py, chunker.py |
| Part 2 | ✅ Done | conflict_detector.py, assembler.py, router.py |
| Part 3 | ✅ Done | api.py, requirements.txt, tests/, HTML UI update |

---

## Integration with existing pipeline

Replace the existing single-file `document_text` string input to Phase 1 with:

```python
from phase0.router import Phase0Router

router = Phase0Router()
doc_context = await router.run(uploaded_files)

# Pass to Phase 1
phase1_input = doc_context.phase_contexts["phase1"]
```

The `source_document` and `page_ref` fields on each chunk flow through to the Phase 1 output,  
giving every extracted requirement full traceability back to the originating RFP document.
