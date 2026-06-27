# RFP Analyzer - Integrated Multi-Document System

## 🚀 Quick Start

### Run the Integrated System

```bash
# 1. Navigate to the analyzer directory
cd rfp-analyzer/analyzer

# 2. Run the integrated web application
python run_integrated.py
```

Open your browser to: **http://localhost:8000**

### Run Phase 0 Standalone

```bash
# 1. Navigate to Phase 0 directory
cd document-consolidator/phase0_router

# 2. Run Phase 0 server
python run_phase0.py
```

Open your browser to: **http://localhost:8001**

## 📋 What's New

### Multi-Document Support

The integrated system now supports uploading and analyzing **multiple RFP documents simultaneously**:

- ✅ Technical specifications
- ✅ Compliance documents  
- ✅ Pricing templates
- ✅ Terms and conditions
- ✅ Reference architectures
- ✅ Statements of work

### Phase 0 Document Router

Automatically processes multiple documents:

1. **Classifies** each document by type with confidence scoring
2. **Chunks** content into semantic sections
3. **Detects conflicts** across documents
4. **Routes** content to appropriate analysis phases
5. **Maintains traceability** back to source documents

### Enhanced Analysis

- **Source Traceability**: Every requirement links to its source document
- **Conflict Detection**: Identifies contradictions between documents
- **Unified Context**: Combines multiple documents into coherent analysis
- **SAP Module Mapping**: Optional mapping to SAP modules for SAP opportunities

## 📁 Project Structure

```
RFxStarterKit-0.1/
├── document-consolidator/
│   └── phase0_router/              # Phase 0 Document Router
│       ├── phase0/                 # Core Phase 0 modules
│       │   ├── api.py             # FastAPI endpoints
│       │   ├── router.py          # Main orchestrator
│       │   ├── classifier.py      # Document classification
│       │   ├── chunker.py         # Content chunking
│       │   ├── conflict_detector.py # Conflict detection
│       │   ├── assembler.py       # Context assembly
│       │   └── schema.py          # Data models
│       ├── run_phase0.py          # Standalone startup script
│       └── requirements.txt       # Phase 0 dependencies
│
├── rfp-analyzer/
│   └── analyzer/                   # RFP Analyzer
│       ├── core/
│       │   ├── ingestor.py        # Document ingestion
│       │   ├── schemas.py         # Data models
│       │   └── phase0_adapter.py  # Phase 0 integration adapter
│       ├── agents/                # Analysis agents
│       │   ├── functional.py      # Functional requirements
│       │   ├── nonfunctional.py   # Non-functional requirements
│       │   ├── compliance.py      # Compliance requirements
│       │   ├── ambiguity.py       # Ambiguity detection
│       │   ├── risk.py            # Risk assessment
│       │   └── synthesizer.py     # Result synthesis
│       ├── outputs/               # Export modules
│       ├── web_app_integrated.py  # Integrated web interface
│       ├── run_integrated.py      # Integrated startup script
│       └── requirements.txt       # Analyzer dependencies
│
├── INTEGRATED_SYSTEM_GUIDE.md     # Comprehensive guide
└── README_INTEGRATED.md           # This file
```

## 🔧 Installation

### Prerequisites

- Python 3.9+
- OpenAI API key (for RFP Analyzer)
- Anthropic API key (for Phase 0)

### Step 1: Install Phase 0 Dependencies

```bash
cd document-consolidator/phase0_router
pip install -r requirements.txt
```

### Step 2: Install RFP Analyzer Dependencies

```bash
cd ../../rfp-analyzer/analyzer
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Create `.env` file in `rfp-analyzer/analyzer/`:

```bash
# Required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional Phase 0 settings
PHASE0_CONFIDENCE_THRESHOLD=0.70
PHASE0_MAX_CHUNKS_PER_DOC=80
```

## 💻 Usage

### Web Interface (Recommended)

1. **Start the integrated server:**
   ```bash
   cd rfp-analyzer/analyzer
   python run_integrated.py
   ```

2. **Open browser to:** http://localhost:8000

3. **Upload documents:**
   - Click "Choose File" or drag & drop
   - Select one or multiple documents
   - Supported formats: PDF, DOCX, TXT, MD, XLSX, CSV

4. **Configure analysis:**
   - Set analysis title
   - Adjust confidence threshold (0.0-1.0)
   - Enable/disable Phase 0 processing
   - Enable SAP module mapping if needed

5. **Start analysis:**
   - Click "Analyze Documents"
   - Monitor progress in real-time
   - Download results when complete

### Command Line Interface

```bash
cd rfp-analyzer/analyzer

# Single document
python main.py analyze path/to/rfp.pdf

# With options
python main.py analyze path/to/rfp.pdf \
  --output-dir ./results \
  --title "Project Alpha" \
  --min-confidence 0.7
```

### Programmatic Usage

```python
import sys
from pathlib import Path

# Add Phase 0 to path
sys.path.insert(0, "../../document-consolidator/phase0_router")

from phase0.router import Phase0Router
from core.phase0_adapter import adapt_phase0_context_to_analyzer

# Process multiple documents with Phase 0
router = Phase0Router()
doc_context = router.run([
    "path/to/rfp_main.pdf",
    "path/to/technical_spec.pdf",
    "path/to/compliance.docx"
])

# Convert to analyzer format
chunks, metadata = adapt_phase0_context_to_analyzer(doc_context, "phase1")

# Access metadata
print(f"RFP ID: {metadata['rfp_id']}")
print(f"Source documents: {metadata['source_documents']}")
print(f"Conflicts detected: {metadata['conflicts_detected']}")

# Continue with analysis...
```

## 📊 Output Formats

The system generates multiple export formats:

### 1. Markdown Report
Human-readable report with all requirements organized by category.

### 2. Excel Spreadsheet
Structured data with:
- Filterable columns
- Requirement categories
- Priority levels
- Source traceability
- SAP module mapping (if enabled)

### 3. JSON Data
Machine-readable format for:
- API integration
- Custom processing
- Data analysis

### 4. HTML (Category View)
Interactive web page with:
- Requirements grouped by category
- Collapsible sections
- Search and filter
- Source document links

### 5. HTML (Module View)
Interactive web page with:
- Requirements grouped by SAP module
- Module-specific views
- Cross-module dependencies

## 🔍 Key Features

### Phase 0 Document Classification

Automatically identifies document types:
- Technical specifications
- Compliance documents
- Pricing templates
- Cover letters
- Reference architectures
- Statements of work
- Terms and conditions

### Intelligent Chunking

Breaks documents into semantic sections:
- Functional requirements
- Non-functional requirements
- Timeline information
- Pricing details
- Compliance clauses
- Architecture notes
- Scope definitions

### Conflict Detection

Identifies contradictions across documents:
- Conflicting requirements
- Inconsistent specifications
- Contradictory constraints
- Severity classification (low/medium/high)

### Source Traceability

Every requirement includes:
- Source document name
- Page reference
- Section heading
- Document type
- Confidence score

### Phase-Aware Routing

Routes content to appropriate analysis phases:
- **Phase 1**: Requirement extraction
- **Phase 2**: Architecture design
- **Phase 3**: Estimation and planning

## 🎯 Use Cases

### Single Document Analysis
Upload one RFP document for standard analysis.

### Multi-Document RFP Pack
Upload complete RFP package with:
- Main RFP document
- Technical appendices
- Compliance checklists
- Pricing templates
- Reference materials

### SAP Opportunity Analysis
Enable SAP module mapping for:
- SAP implementation projects
- SAP migration projects
- SAP enhancement projects

### Conflict Resolution
Identify and resolve contradictions between:
- Multiple RFP versions
- Technical specs vs. compliance docs
- Client requirements vs. constraints

## 🔧 Configuration

### Phase 0 Settings

```bash
# Document classification confidence threshold
PHASE0_CONFIDENCE_THRESHOLD=0.70

# Maximum chunks per document
PHASE0_MAX_CHUNKS_PER_DOC=80
```

### RFP Analyzer Settings

```bash
# Minimum confidence for requirement extraction
MIN_CONFIDENCE=0.0

# Enable/disable specific agents
ENABLE_FUNCTIONAL=true
ENABLE_NONFUNCTIONAL=true
ENABLE_COMPLIANCE=true
ENABLE_AMBIGUITY=true
ENABLE_RISK=true
```

## 📚 Documentation

- **[INTEGRATED_SYSTEM_GUIDE.md](./INTEGRATED_SYSTEM_GUIDE.md)** - Comprehensive integration guide
- **[document-consolidator/phase0_router/README.md](./document-consolidator/phase0_router/README.md)** - Phase 0 documentation
- **[rfp-analyzer/analyzer/README.md](./rfp-analyzer/analyzer/README.md)** - RFP Analyzer documentation

## 🐛 Troubleshooting

### Phase 0 Not Available

If Phase 0 is not detected:

1. Verify installation:
   ```bash
   cd document-consolidator/phase0_router
   pip install -r requirements.txt
   ```

2. Check ANTHROPIC_API_KEY is set

3. System will fall back to standard ingestion

### Import Errors

Ensure you're running from the correct directory:
```bash
cd rfp-analyzer/analyzer
python run_integrated.py
```

### Memory Issues

For large document sets:
- Reduce `PHASE0_MAX_CHUNKS_PER_DOC`
- Process documents in smaller batches
- Increase system memory

## 🔐 API Endpoints

### Integrated System

- `POST /api/analyze` - Upload and analyze documents
- `GET /api/status/{job_id}` - Check analysis status
- `GET /api/results/{job_id}` - Get analysis results
- `GET /api/download/{job_id}/{file_type}` - Download exports
- `GET /health` - Health check

### Phase 0 Standalone

- `POST /phase0/analyze` - Process multiple documents
- `GET /health` - Health check
- `GET /docs` - API documentation

## 📈 Performance

### Typical Processing Times

- **Single document (10 pages)**: 2-3 minutes
- **Multi-document pack (5 docs, 50 pages)**: 5-8 minutes
- **Large RFP (100+ pages)**: 10-15 minutes

### Optimization Tips

1. Use appropriate confidence thresholds
2. Enable Phase 0 only for multiple documents
3. Process documents in batches for large sets
4. Use caching for repeated analyses

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

- Phase 0 Document Router - Multi-document processing
- RFP Analyzer - AI-powered requirement extraction
- OpenAI GPT-4 - Language model for analysis
- Anthropic Claude - Language model for classification

## 📞 Support

For issues or questions:

1. Check the logs in `rfp-analyzer/analyzer/logs/`
2. Review documentation in `INTEGRATED_SYSTEM_GUIDE.md`
3. Open an issue on GitHub

---

**Version**: 3.0.0  
**Last Updated**: 2026-06-20  
**Status**: Production Ready ✅