# RFP Analyzer - Integrated Multi-Document System Guide

## Overview

This guide explains how to use the integrated RFP Analyzer system that combines:
- **Phase 0 Document Router**: Multi-document classification, chunking, and conflict detection
- **RFP Analyzer**: AI-powered requirement extraction and analysis

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Upload Interface                     │
│              (Multiple Documents Supported)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Phase 0 Document Router                    │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────────┐   │
│  │ Classifier   │→ │ Chunker  │→ │ Conflict Detector  │   │
│  └──────────────┘  └──────────┘  └────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│              ┌──────────────────────┐                       │
│              │ Context Assembler    │                       │
│              └──────────────────────┘                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Phase 0 Adapter                           │
│         (Converts to RFP Analyzer format)                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    RFP Analyzer Pipeline                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Functional│→ │Non-Func  │→ │Compliance│→ │Ambiguity │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                         │                                    │
│                         ▼                                    │
│              ┌──────────────────────┐                       │
│              │    Synthesizer       │                       │
│              └──────────────────────┘                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Export & Results                            │
│     (Markdown, Excel, JSON, HTML)                            │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
# Install Phase 0 dependencies
cd document-consolidator/phase0_router
pip install -r requirements.txt

# Install RFP Analyzer dependencies
cd ../../rfp-analyzer/analyzer
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in `rfp-analyzer/analyzer/`:

```bash
# Required for RFP Analyzer
OPENAI_API_KEY=sk-...

# Required for Phase 0
ANTHROPIC_API_KEY=sk-ant-...

# Optional Phase 0 settings
PHASE0_CONFIDENCE_THRESHOLD=0.70
PHASE0_MAX_CHUNKS_PER_DOC=80
```

### 3. Run the Integrated System

```bash
cd rfp-analyzer/analyzer
python run_integrated.py
```

Or with custom settings:

```bash
python run_integrated.py --host 0.0.0.0 --port 8080 --reload
```

### 4. Access the Web Interface

Open your browser to: `http://localhost:8000`

## Features

### Multi-Document Support

Upload multiple RFP documents simultaneously:
- Technical specifications
- Compliance documents
- Pricing templates
- Terms and conditions
- Reference architectures
- Statements of work

### Phase 0 Processing

When multiple documents are uploaded, Phase 0 automatically:

1. **Classifies** each document by type
2. **Chunks** content into semantic sections
3. **Detects conflicts** across documents
4. **Routes** content to appropriate analysis phases
5. **Provides traceability** back to source documents

### Document Types Supported

- PDF (`.pdf`)
- Word Documents (`.docx`, `.doc`)
- Text Files (`.txt`)
- Markdown (`.md`)
- Excel (`.xlsx`)
- CSV (`.csv`)

### Analysis Outputs

The system generates multiple export formats:

1. **Markdown** - Human-readable report
2. **Excel** - Structured spreadsheet with filtering
3. **JSON** - Machine-readable data
4. **HTML (Category)** - Interactive web view by requirement category
5. **HTML (Module)** - Interactive web view by SAP module (if enabled)

## Usage Scenarios

### Scenario 1: Single Document Analysis

1. Upload one RFP document
2. System uses standard ingestion (Phase 0 bypassed)
3. Analysis proceeds normally
4. Results exported in all formats

### Scenario 2: Multi-Document RFP Pack

1. Upload multiple related documents:
   - Main RFP document
   - Technical appendix
   - Compliance checklist
   - Pricing template

2. Phase 0 processes documents:
   - Classifies each by type
   - Extracts and chunks content
   - Detects any conflicts between documents
   - Assembles unified context

3. RFP Analyzer processes unified context:
   - Extracts requirements from all documents
   - Maintains source traceability
   - Flags conflicts for review

4. Results include:
   - All requirements with source document references
   - Conflict warnings where applicable
   - Document classification metadata

### Scenario 3: SAP Opportunity Analysis

1. Enable "SAP Opportunity" checkbox
2. Upload RFP documents
3. System performs standard analysis
4. Additionally maps requirements to SAP modules
5. HTML export includes SAP module grouping

## API Endpoints

### POST `/api/analyze`

Upload and analyze documents.

**Form Data:**
- `files`: Multiple file uploads
- `title`: Analysis title (default: "RFP Analysis")
- `org_context_url`: Optional organizational context URL
- `min_confidence`: Minimum confidence threshold (0.0-1.0)
- `use_phase0`: Enable Phase 0 processing (default: true)
- `is_sap_opp`: Enable SAP module mapping (default: false)

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Analysis started for N file(s)"
}
```

### GET `/api/status/{job_id}`

Check analysis status.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 75,
  "current_step": "Extracting functional requirements",
  "status_detail": "Running functional extraction across 45 chunks",
  "phase0_metadata": {
    "rfp_id": "RFP-ABC123",
    "documents": [...],
    "conflicts_detected": 2
  }
}
```

### GET `/api/results/{job_id}`

Get analysis results.

**Response:**
```json
{
  "job_id": "uuid",
  "title": "RFP Analysis",
  "requirements": [...],
  "phase0_metadata": {...},
  "exports": {
    "markdown": "path/to/file.md",
    "excel": "path/to/file.xlsx",
    "json": "path/to/file.json",
    "html_category": "path/to/file_by_category.html",
    "html_module": "path/to/file_by_module.html"
  }
}
```

### GET `/api/download/{job_id}/{file_type}`

Download exported file.

**File Types:**
- `markdown`
- `excel`
- `json`
- `html_category`
- `html_module`

### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "3.0.0",
  "phase0_available": true,
  "active_jobs": 2
}
```

## Phase 0 Standalone Usage

You can also run Phase 0 independently:

```bash
cd document-consolidator/phase0_router
uvicorn phase0.api:app --reload --port 8001
```

Access at: `http://localhost:8001`

### Phase 0 API

**POST `/phase0/analyze`**

Upload multiple documents for classification and routing.

**Response:**
```json
{
  "success": true,
  "rfp_id": "RFP-ABC123",
  "document_context": {
    "documents": [...],
    "phase_contexts": {...},
    "conflicts": [...],
    "metadata": {...}
  },
  "warnings": []
}
```

## Configuration

### Phase 0 Settings

Environment variables for Phase 0:

```bash
# Confidence threshold for document classification
PHASE0_CONFIDENCE_THRESHOLD=0.70

# Maximum chunks per document
PHASE0_MAX_CHUNKS_PER_DOC=80

# Anthropic API key (required)
ANTHROPIC_API_KEY=sk-ant-...
```

### RFP Analyzer Settings

Environment variables for RFP Analyzer:

```bash
# OpenAI API key (required)
OPENAI_API_KEY=sk-...

# Optional: Organizational context
ORG_CONTEXT_PATH=path/to/context.yaml
```

## Troubleshooting

### Phase 0 Not Available

If you see "Phase 0 not available" warning:

1. Check Phase 0 installation:
   ```bash
   cd document-consolidator/phase0_router
   pip install -r requirements.txt
   ```

2. Verify ANTHROPIC_API_KEY is set

3. System will fall back to standard ingestion

### Import Errors

If you encounter import errors:

1. Ensure you're running from the correct directory:
   ```bash
   cd rfp-analyzer/analyzer
   python run_integrated.py
   ```

2. Check Python path includes Phase 0:
   ```python
   import sys
   from pathlib import Path
   phase0_path = Path("../../document-consolidator/phase0_router")
   sys.path.insert(0, str(phase0_path))
   ```

### Memory Issues

For large document sets:

1. Reduce `PHASE0_MAX_CHUNKS_PER_DOC`
2. Process documents in smaller batches
3. Increase system memory allocation

## Best Practices

### Document Organization

1. **Name files descriptively**: `technical_spec.pdf`, `compliance_checklist.docx`
2. **Group related documents**: Upload all documents for one RFP together
3. **Include metadata**: Use clear section headings in documents

### Analysis Configuration

1. **Set appropriate confidence threshold**: 0.7-0.8 for most cases
2. **Enable Phase 0 for multiple documents**: Provides better context
3. **Use SAP mapping for SAP projects**: Improves requirement organization

### Review Process

1. **Check Phase 0 metadata**: Review document classifications
2. **Address conflicts**: Resolve contradictions between documents
3. **Verify traceability**: Ensure requirements link to source documents
4. **Export multiple formats**: Use different formats for different audiences

## Integration with Existing Workflows

### Programmatic Usage

```python
from pathlib import Path
import sys

# Add Phase 0 to path
sys.path.insert(0, "../../document-consolidator/phase0_router")

from phase0.router import Phase0Router
from core.phase0_adapter import adapt_phase0_context_to_analyzer
from core.ingestor import ingest_document

# Process multiple documents
router = Phase0Router()
doc_context = router.run([
    "path/to/rfp_main.pdf",
    "path/to/technical_spec.pdf",
    "path/to/compliance.docx"
])

# Convert to analyzer format
chunks, metadata = adapt_phase0_context_to_analyzer(doc_context, "phase1")

# Continue with RFP analysis...
```

### CI/CD Integration

```yaml
# Example GitHub Actions workflow
name: RFP Analysis
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: |
          pip install -r document-consolidator/phase0_router/requirements.txt
          pip install -r rfp-analyzer/analyzer/requirements.txt
      - name: Run analysis
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd rfp-analyzer/analyzer
          python -c "from web_app_integrated import run_integrated_analysis; ..."
```

## Support

For issues or questions:

1. Check the logs in `rfp-analyzer/analyzer/logs/`
2. Review Phase 0 documentation: `document-consolidator/phase0_router/README.md`
3. Review RFP Analyzer documentation: `rfp-analyzer/analyzer/README.md`

## Version History

- **v3.0.0** - Integrated multi-document system with Phase 0
- **v2.0.0** - Enhanced RFP Analyzer with SAP mapping
- **v1.0.0** - Initial RFP Analyzer release