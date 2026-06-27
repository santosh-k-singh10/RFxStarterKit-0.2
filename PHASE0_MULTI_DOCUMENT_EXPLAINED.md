# Phase 0: Multi-Document RFP Processing Explained

## Overview

Phase 0 (Document Consolidator) is a pre-processing layer that sits **before** the main RFP Analyzer. It solves a critical problem: **How do you analyze RFPs that come as multiple documents instead of a single file?**

### The Problem

Real-world RFPs often arrive as packages containing:
- Main RFP document (PDF)
- Technical specifications (DOCX)
- Compliance checklist (DOCX)
- Pricing template (XLSX)
- Terms and conditions (PDF)
- Reference architecture diagrams (PDF)
- Corrigendum/amendments (PDF)

**Challenges:**
1. Each document has different content types
2. Information may be duplicated across documents
3. Documents may contradict each other
4. Requirements are scattered across multiple files
5. Need to maintain traceability to source documents

### The Solution: Phase 0

Phase 0 acts as an intelligent router that:
1. **Classifies** each document by type
2. **Chunks** content into semantic sections
3. **Detects conflicts** between documents
4. **Assembles** unified context for downstream analysis
5. **Maintains traceability** back to source documents

---

## How Phase 0 Works: Step-by-Step

### Step 1: Document Upload

**User Action:**
```
Upload multiple files:
├── RFP-Main-Document.pdf
├── Technical-Specifications.docx
├── Compliance-Requirements.docx
└── Pricing-Template.xlsx
```

**System Receives:**
- 4 files via multipart/form-data
- Each file is temporarily stored
- Metadata extracted (filename, size, type)

---

### Step 2: Document Classification

**What Happens:**
The Classifier agent analyzes each document to determine its type.

**Process:**
```python
# For each document
1. Extract first few pages/sections
2. Send to  AI with classification prompt
3. AI analyzes content and structure
4. Returns document type + confidence score
```

**Example Output:**
```json
{
  "filename": "RFP-Main-Document.pdf",
  "doc_type": "technical_specification",
  "confidence": 0.94,
  "pages": 45,
  "reasoning": "Contains detailed technical requirements, system architecture, and functional specifications"
}
```

**Document Types Detected:**
- `technical_specification` - Technical requirements, architecture
- `compliance_document` - Regulatory, legal, standards
- `pricing_template` - Cost breakdown, pricing models
- `terms_conditions` - Legal terms, contracts
- `reference_architecture` - Diagrams, design patterns
- `statement_of_work` - Project scope, deliverables
- `corrigendum` - Amendments, updates to original RFP

**Why This Matters:**
Different document types need different processing strategies. Technical specs need detailed chunking, while pricing templates need tabular data extraction.

---

### Step 3: Semantic Chunking

**What Happens:**
The Chunker agent breaks each document into meaningful sections while preserving context.

**Process:**
```python
# For each document
1. Parse document structure (headings, sections, tables)
2. Identify section boundaries
3. Extract content with context
4. Tag each chunk with metadata
5. Determine phase relevance
```

**Example: Technical Specification Document**

**Original Document Structure:**
```
1. Introduction
2. System Requirements
   2.1 Functional Requirements
   2.2 Non-Functional Requirements
3. Technical Architecture
   3.1 System Components
   3.2 Integration Points
4. Security Requirements
5. Compliance Requirements
```

**Chunked Output:**
```json
[
  {
    "chunk_id": "ch_001",
    "source_document": "Technical-Specifications.docx",
    "page_ref": "p.1-2",
    "doc_type": "technical_specification",
    "section_type": "introduction",
    "phase_relevance": ["phase1"],
    "content": "This document outlines the technical requirements..."
  },
  {
    "chunk_id": "ch_002",
    "source_document": "Technical-Specifications.docx",
    "page_ref": "p.3-5",
    "doc_type": "technical_specification",
    "section_type": "functional_requirement",
    "phase_relevance": ["phase1", "phase2"],
    "content": "2.1 Functional Requirements\nFR-001: User Authentication\nThe system must provide secure user authentication..."
  },
  {
    "chunk_id": "ch_003",
    "source_document": "Technical-Specifications.docx",
    "page_ref": "p.6-8",
    "doc_type": "technical_specification",
    "section_type": "non_functional_requirement",
    "phase_relevance": ["phase1"],
    "content": "2.2 Non-Functional Requirements\nNFR-001: Performance\nThe system must handle 10,000 concurrent users..."
  }
]
```

**Phase Relevance Tags:**
- `phase1` - Requirement extraction (RFP Analyzer)
- `phase2` - Architecture design (Scoping Architect)
- `phase3` - Implementation planning (future)

**Why This Matters:**
- Maintains context within sections
- Preserves document structure
- Enables targeted routing to specific analysis phases
- Keeps chunks at optimal size (not too small, not too large)

---

### Step 4: Conflict Detection

**What Happens:**
The Conflict Detector compares chunks across documents to find contradictions.

**Process:**
```python
# Compare all chunks pairwise
1. Group chunks by topic/requirement
2. Use AI to detect contradictions
3. Flag conflicts with severity
4. Link conflicting chunks
```

**Example Conflict Scenarios:**

**Scenario 1: Timeline Conflict**
```
Document A (Main RFP):
"Project must be completed within 6 months"

Document B (Corrigendum):
"Updated timeline: Project completion extended to 9 months"

Conflict Detected:
{
  "conflict_id": "C001",
  "type": "timeline_discrepancy",
  "severity": "high",
  "chunk_ids": ["ch_015", "ch_087"],
  "description": "Timeline conflict: Main RFP states 6 months, Corrigendum extends to 9 months",
  "resolution_needed": true,
  "recommended_action": "Use Corrigendum timeline (9 months) as it's the latest update"
}
```

**Scenario 2: Technical Requirement Conflict**
```
Document A (Technical Spec):
"System must support 1,000 concurrent users"

Document B (Compliance Doc):
"System must support minimum 5,000 concurrent users for compliance"

Conflict Detected:
{
  "conflict_id": "C002",
  "type": "requirement_contradiction",
  "severity": "critical",
  "chunk_ids": ["ch_023", "ch_056"],
  "description": "Performance requirement conflict: Technical spec says 1,000 users, Compliance requires 5,000",
  "resolution_needed": true,
  "recommended_action": "Use higher requirement (5,000 users) to meet compliance"
}
```

**Scenario 3: Budget Discrepancy**
```
Document A (Main RFP):
"Total budget: $500,000"

Document B (Pricing Template):
"Budget allocation: $750,000"

Conflict Detected:
{
  "conflict_id": "C003",
  "type": "budget_mismatch",
  "severity": "high",
  "chunk_ids": ["ch_008", "ch_092"],
  "description": "Budget conflict: Main RFP states $500K, Pricing template shows $750K",
  "resolution_needed": true,
  "recommended_action": "Clarify with client which budget is correct"
}
```

**Why This Matters:**
- Prevents analysis based on contradictory information
- Highlights areas needing clarification
- Ensures compliance with latest updates
- Reduces risk of incorrect assumptions

---

### Step 5: Context Assembly

**What Happens:**
The Context Assembler creates unified context objects for each downstream phase.

**Process:**
```python
# For each phase (phase1, phase2, phase3)
1. Collect all chunks tagged for that phase
2. Group by document type
3. Attach conflict warnings
4. Add metadata and statistics
5. Create phase-specific context object
```

**Example: Phase 1 Context (for RFP Analyzer)**

```json
{
  "phase": "phase1",
  "chunks": [
    {
      "chunk_id": "ch_002",
      "content": "FR-001: User Authentication...",
      "source_document": "Technical-Specifications.docx",
      "page_ref": "p.3-5",
      "doc_type": "technical_specification",
      "conflict_flag": false
    },
    {
      "chunk_id": "ch_015",
      "content": "Project timeline: 6 months...",
      "source_document": "RFP-Main-Document.pdf",
      "page_ref": "p.12",
      "doc_type": "technical_specification",
      "conflict_flag": true,
      "conflict_ref": "C001"
    },
    {
      "chunk_id": "ch_056",
      "content": "Compliance requirement: 5,000 users...",
      "source_document": "Compliance-Requirements.docx",
      "page_ref": "p.8",
      "doc_type": "compliance_document",
      "conflict_flag": true,
      "conflict_ref": "C002"
    }
  ],
  "metadata": {
    "total_chunks": 87,
    "documents_included": 4,
    "conflict_count": 2
  }
}
```

**Why This Matters:**
- Each phase gets exactly the content it needs
- Reduces processing time (no irrelevant content)
- Maintains full traceability
- Conflict warnings travel with the data

---

### Step 6: Final Output - Document Context

**What Happens:**
Phase 0 produces a complete `document_context` object that contains everything needed for downstream analysis.

**Complete Output Structure:**

```json
{
  "rfp_id": "RFP-2024-HC-002",
  "timestamp": "2026-06-21T16:30:00Z",
  
  "documents": [
    {
      "filename": "RFP-Main-Document.pdf",
      "doc_type": "technical_specification",
      "confidence": 0.94,
      "pages": 45,
      "chunks_generated": 32
    },
    {
      "filename": "Technical-Specifications.docx",
      "doc_type": "technical_specification",
      "confidence": 0.98,
      "pages": 28,
      "chunks_generated": 25
    },
    {
      "filename": "Compliance-Requirements.docx",
      "doc_type": "compliance_document",
      "confidence": 0.91,
      "pages": 15,
      "chunks_generated": 18
    },
    {
      "filename": "Pricing-Template.xlsx",
      "doc_type": "pricing_template",
      "confidence": 0.89,
      "pages": 5,
      "chunks_generated": 12
    }
  ],
  
  "phase_contexts": {
    "phase1": [
      /* 87 chunks for requirement extraction */
    ],
    "phase2": [
      /* 45 chunks for architecture design */
    ],
    "phase3": [
      /* 23 chunks for implementation planning */
    ]
  },
  
  "conflicts": [
    {
      "conflict_id": "C001",
      "type": "timeline_discrepancy",
      "severity": "high",
      "chunk_ids": ["ch_015", "ch_087"],
      "description": "Timeline conflict between main RFP and corrigendum",
      "resolution_needed": true
    },
    {
      "conflict_id": "C002",
      "type": "requirement_contradiction",
      "severity": "critical",
      "chunk_ids": ["ch_023", "ch_056"],
      "description": "Performance requirement conflict",
      "resolution_needed": true
    }
  ],
  
  "metadata": {
    "total_docs": 4,
    "total_chunks": 87,
    "conflict_count": 2,
    "processing_time_seconds": 45.3,
    "confidence_avg": 0.93
  },
  
  "warnings": [
    "2 conflicts detected requiring resolution",
    "Corrigendum updates found - using latest information"
  ]
}
```

---

## Integration with RFP Analyzer (Phase 1)

### Phase 0 Adapter

**Location:** `rfp-analyzer/analyzer/core/phase0_adapter.py`

**Purpose:** Convert Phase 0 output to RFP Analyzer input format

**Transformation:**

```python
# Input: Phase 0 document_context
phase0_output = {
  "phase_contexts": {
    "phase1": [chunks]
  },
  "conflicts": [conflicts],
  "metadata": {...}
}

# Output: RFP Analyzer DocumentChunk[]
analyzer_chunks = [
  DocumentChunk(
    chunk_id="ch_001",
    content="...",
    source_section="Functional Requirements",
    source_document="Technical-Specifications.docx",
    page_ref="p.3-5",
    metadata={
      "doc_type": "technical_specification",
      "conflict_flag": false,
      "phase0_processed": true
    }
  )
]
```

**What the Adapter Does:**
1. Extracts phase1 chunks from document_context
2. Converts to DocumentChunk format
3. Preserves all metadata and traceability
4. Attaches conflict warnings
5. Adds Phase 0 processing flag

---

## Complete Flow Example

### Scenario: Healthcare RFP Package

**Input Documents:**
```
1. RFP-2026-HC-002-HIMS-Original.docx (Main RFP)
2. RFP-2026-HC-002-Overview-Original.pdf (Overview)
3. RFP-2026-HC-002-Corrigendum-1.docx (Update 1)
4. RFP-2026-HC-002-Corrigendum-2.pdf (Update 2)
5. RFP-2026-HC-002-Cost-Original.xlsx (Pricing)
```

### Phase 0 Processing

**Step 1: Classification**
```
Document 1: technical_specification (0.96)
Document 2: technical_specification (0.89)
Document 3: corrigendum (0.94)
Document 4: corrigendum (0.91)
Document 5: pricing_template (0.88)
```

**Step 2: Chunking**
```
Document 1: 45 chunks
Document 2: 23 chunks
Document 3: 8 chunks (updates)
Document 4: 5 chunks (updates)
Document 5: 12 chunks (pricing)
Total: 93 chunks
```

**Step 3: Conflict Detection**
```
Conflict C001: Timeline updated in Corrigendum-1
Conflict C002: Budget revised in Corrigendum-2
Conflict C003: Technical requirement clarified in Corrigendum-1
Total: 3 conflicts detected
```

**Step 4: Context Assembly**
```
Phase 1 context: 87 chunks (requirement extraction)
Phase 2 context: 45 chunks (architecture design)
Phase 3 context: 23 chunks (implementation)
```

**Step 5: Output**
```json
{
  "rfp_id": "RFP-2026-HC-002",
  "documents": 5,
  "chunks": 93,
  "conflicts": 3,
  "ready_for_analysis": true
}
```

### RFP Analyzer Processing

**Input from Phase 0:**
- 87 chunks for Phase 1
- All chunks have source traceability
- 3 conflict warnings attached

**Analysis:**
```
Functional Agent: Extracts 34 functional requirements
  - FR-001 from chunk ch_012 (Document 1, p.5)
  - FR-002 from chunk ch_023 (Document 1, p.8)
  - FR-003 from chunk ch_045 (Document 2, p.3)
  
Non-Functional Agent: Extracts 18 NFRs
  - NFR-001 from chunk ch_034 (Document 1, p.12)
  - NFR-002 from chunk ch_056 (Document 2, p.7)
  
Compliance Agent: Extracts 12 compliance requirements
  - CR-001 from chunk ch_067 (Document 1, p.18)
  
Ambiguity Agent: Flags 5 ambiguities
  - AMB-001 from chunk ch_015 (conflict C001)
  
Risk Agent: Identifies 3 risks
  - RISK-001 from chunk ch_023 (conflict C002)
```

**Output:**
```
Total Requirements: 72
  - 34 Functional
  - 18 Non-Functional
  - 12 Compliance
  - 5 Ambiguities
  - 3 Risks

All requirements include:
  - Source document reference
  - Page number
  - Conflict warnings (if applicable)
  - Confidence score
```

---

## Benefits of Phase 0

### 1. **Handles Complexity**
- Processes multiple documents simultaneously
- Maintains organization across files
- Preserves document relationships

### 2. **Ensures Accuracy**
- Detects contradictions automatically
- Uses latest information (corrigenda)
- Flags areas needing clarification

### 3. **Maintains Traceability**
- Every requirement links to source document
- Page references preserved
- Audit trail for compliance

### 4. **Improves Efficiency**
- Automated classification
- Intelligent routing
- Reduces manual review time

### 5. **Reduces Risk**
- Conflict detection prevents errors
- Ensures nothing is missed
- Highlights critical issues

---

## When to Use Phase 0

### ✅ Use Phase 0 When:
- RFP comes as multiple documents
- Documents include corrigenda/amendments
- Need to track source of requirements
- Want automatic conflict detection
- Processing complex RFP packages

### ❌ Skip Phase 0 When:
- Single document RFP
- Simple, straightforward requirements
- No risk of conflicts
- Speed is critical (Phase 0 adds processing time)

---

## Technical Implementation

### API Usage

**Standalone Phase 0:**
```bash
# Start Phase 0 server
cd document-consolidator/phase0_router
python run_phase0.py

# Upload documents
curl -X POST http://localhost:8001/phase0/analyze \
  -F "documents=@RFP-Main.pdf" \
  -F "documents=@Technical-Spec.docx" \
  -F "documents=@Compliance.docx"

# Response: document_context JSON
```

**Integrated with RFP Analyzer:**
```bash
# Start integrated system
cd rfp-analyzer/analyzer
python run_integrated.py

# Upload documents (Phase 0 runs automatically)
curl -X POST http://localhost:8000/api/analyze \
  -F "files=@RFP-Main.pdf" \
  -F "files=@Technical-Spec.docx" \
  -F "use_phase0=true"
```

### Programmatic Usage

```python
from phase0.router import Phase0Router
from core.phase0_adapter import adapt_phase0_context_to_analyzer

# Initialize Phase 0
router = Phase0Router()

# Process documents
doc_context = await router.run([
    "RFP-Main.pdf",
    "Technical-Spec.docx",
    "Compliance.docx"
])

# Convert to RFP Analyzer format
chunks, metadata = adapt_phase0_context_to_analyzer(
    doc_context, 
    phase="phase1"
)

# Continue with RFP analysis
# ... run RFP Analyzer with chunks
```

---

## Configuration

### Environment Variables

```bash
# Phase 0 Configuration
ANTHROPIC_API_KEY=sk-ant-...
PHASE0_CONFIDENCE_THRESHOLD=0.70
PHASE0_MAX_CHUNKS_PER_DOC=80

# Optional
PHASE0_ENABLE_CONFLICT_DETECTION=true
PHASE0_CONFLICT_SEVERITY_THRESHOLD=medium
```

### Tuning Parameters

**Confidence Threshold:**
- `0.60-0.70` - Lenient (accepts more classifications)
- `0.70-0.80` - Balanced (recommended)
- `0.80-0.90` - Strict (only high-confidence classifications)

**Max Chunks Per Document:**
- `50-60` - Fast processing, less detail
- `80-100` - Balanced (recommended)
- `100+` - Detailed analysis, slower processing

---

## Troubleshooting

### Issue: Documents Not Classified Correctly

**Symptoms:**
- Wrong document type assigned
- Low confidence scores

**Solutions:**
1. Check document quality (scanned vs native PDF)
2. Ensure documents have clear structure
3. Lower confidence threshold
4. Review classification prompt

### Issue: Too Many Conflicts Detected

**Symptoms:**
- False positive conflicts
- Conflicts on minor differences

**Solutions:**
1. Increase conflict severity threshold
2. Review conflict detection prompt
3. Filter conflicts by severity
4. Manual review of flagged conflicts

### Issue: Slow Processing

**Symptoms:**
- Long processing time
- Timeout errors

**Solutions:**
1. Reduce max chunks per document
2. Process documents in batches
3. Increase API rate limits
4. Use faster LLM model

---

## Summary

Phase 0 transforms the challenge of multi-document RFP analysis into a structured, automated process:

1. **Classifies** documents by type
2. **Chunks** content semantically
3. **Detects** conflicts across documents
4. **Assembles** unified context
5. **Maintains** complete traceability

The result is a clean, organized input for the RFP Analyzer that ensures accurate, comprehensive requirement extraction with full source traceability.

---

**Key Takeaway:** Phase 0 is like having an intelligent assistant who reads all your RFP documents, organizes them, highlights conflicts, and prepares a perfect summary for analysis - automatically.

---

*For more details, see:*
- `INTEGRATED_SYSTEM_GUIDE.md` - Complete integration guide
- `document-consolidator/phase0_router/README.md` - Phase 0 technical details
- `COMPLETE_END_TO_END_ARCHITECTURE.md` - Full system architecture