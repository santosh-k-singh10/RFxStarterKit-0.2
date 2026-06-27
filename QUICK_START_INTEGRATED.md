# Quick Start Guide: Integrated RFP Analyzer + Phase 0

## Overview

This integrated system combines:
- **Phase 0 Document Router**: Multi-document classification and conflict detection
- **RFP Analyzer**: AI-powered requirement extraction and analysis

## Prerequisites

1. **Python 3.9+** installed
2. **API Keys** configured in `rfp-analyzer/.env`:
   ```env
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here  # Optional, for Phase 0
   ```

## Installation

### 1. Install Dependencies

```bash
# Install RFP Analyzer dependencies
cd rfp-analyzer/analyzer
pip install -r requirements.txt

# Install Phase 0 dependencies (optional, for multi-document support)
cd ../../document-consolidator/phase0_router
pip install -r requirements.txt
```

### 2. Configure Environment

Create `rfp-analyzer/.env` file:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...  # Optional
```

## Running the Application

### Option 1: Quick Start (Recommended)

**Windows:**
```cmd
cd rfp-analyzer\analyzer
START_INTEGRATED.bat
```

**Linux/Mac:**
```bash
cd rfp-analyzer/analyzer
./START_INTEGRATED.sh
```

### Option 2: Manual Start

```bash
cd rfp-analyzer/analyzer
python run_webapp.py --host 0.0.0.0 --port 8000
```

### Option 3: Alternative Integrated Version

```bash
cd rfp-analyzer/analyzer
python run_integrated.py --host 0.0.0.0 --port 8000
```

## Using the Application

1. **Open Browser**: Navigate to `http://localhost:8000`

2. **Upload Documents**:
   - **Single Document**: Upload one RFP file for standard analysis
   - **Multiple Documents**: Upload multiple files for Phase 0 classification
     - Supported formats: PDF, DOCX, TXT, MD, XLSX, CSV

3. **Analysis Process**:
   - **With Phase 0** (multiple files + ANTHROPIC_API_KEY set):
     - Documents are classified by type
     - Conflicts are detected
     - Unified context is created
     - RFP analysis proceeds
   
   - **Without Phase 0** (single file OR no ANTHROPIC_API_KEY):
     - Standard document ingestion
     - Direct RFP analysis

4. **View Results**:
   - Requirements extracted by category
   - Compliance items identified
   - Risks and ambiguities highlighted
   - Export to Excel, JSON, or HTML

## Features

### Single Document Mode
- Standard RFP analysis
- Requirement extraction
- Compliance checking
- Risk assessment

### Multi-Document Mode (Phase 0 Enabled)
- Automatic document classification
- Conflict detection across documents
- Document type identification (RFP, SOW, Technical Specs, etc.)
- Unified document context
- Source traceability

## Troubleshooting

### Phase 0 Not Available
**Symptom**: Multi-document upload works but uses standard ingestion

**Causes**:
1. `ANTHROPIC_API_KEY` not set in `.env`
2. Phase 0 dependencies not installed
3. Phase 0 directory not found

**Solution**:
```bash
# Check if Phase 0 is available
cd document-consolidator/phase0_router
pip install -r requirements.txt

# Add API key to rfp-analyzer/.env
echo "ANTHROPIC_API_KEY=sk-ant-..." >> rfp-analyzer/.env
```

### Import Errors
**Symptom**: `ModuleNotFoundError` when starting

**Solution**:
```bash
# Ensure you're in the correct directory
cd rfp-analyzer/analyzer

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use
**Symptom**: `Address already in use` error

**Solution**:
```bash
# Use a different port
python run_webapp.py --port 8001
```

## API Endpoints

### Upload and Analyze
```http
POST /api/analyze
Content-Type: multipart/form-data

files: [file1, file2, ...]  # Multiple files supported
title: "My RFP Analysis"
org_context_url: "optional_url"
min_confidence: 0.0
```

### Check Status
```http
GET /api/status/{job_id}
```

### Download Results
```http
GET /api/download/{job_id}/{format}
```
Formats: `excel`, `json`, `html`, `markdown`

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface                         │
│                  (web_app.py:8000)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ├─ Single File ──────────────────────┐
                     │                                     │
                     ├─ Multiple Files ───────────────┐   │
                     │                                 │   │
                     ▼                                 ▼   ▼
          ┌──────────────────────┐         ┌─────────────────┐
          │   Phase 0 Router     │         │  Standard       │
          │  (Classification)    │         │  Ingestion      │
          └──────────┬───────────┘         └────────┬────────┘
                     │                              │
                     ├─ Document Classification     │
                     ├─ Conflict Detection          │
                     ├─ Chunk Assembly              │
                     │                              │
                     ▼                              │
          ┌──────────────────────┐                 │
          │  Phase 0 Adapter     │                 │
          │  (Format Conversion) │                 │
          └──────────┬───────────┘                 │
                     │                              │
                     └──────────────┬───────────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │   RFP Analyzer Engine    │
                     │  (Multi-Agent System)    │
                     └──────────────────────────┘
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │Functional│   │Compliance│   │   Risk   │
              │  Agent   │   │  Agent   │   │  Agent   │
              └──────────┘   └──────────┘   └──────────┘
                                    │
                                    ▼
                     ┌──────────────────────────┐
                     │    Export Results        │
                     │ (Excel/JSON/HTML/MD)     │
                     └──────────────────────────┘
```

## File Structure

```
RFxStarterKit-0.1/
├── document-consolidator/
│   └── phase0_router/              # Phase 0 Document Router
│       ├── phase0/
│       │   ├── router.py           # Main router
│       │   ├── classifier.py       # Document classification
│       │   ├── chunker.py          # Document chunking
│       │   ├── conflict_detector.py # Conflict detection
│       │   └── assembler.py        # Context assembly
│       └── requirements.txt
│
├── rfp-analyzer/
│   ├── .env                        # API keys (create this)
│   └── analyzer/
│       ├── web_app.py              # Main web interface (ENHANCED)
│       ├── run_webapp.py           # Startup script
│       ├── run_integrated.py       # Alternative startup
│       ├── START_INTEGRATED.bat    # Windows quick start
│       ├── START_INTEGRATED.sh     # Linux/Mac quick start
│       ├── core/
│       │   ├── phase0_adapter.py   # Phase 0 ↔ Analyzer bridge
│       │   └── ingestor.py         # Standard ingestion
│       └── requirements.txt
│
├── INTEGRATED_SYSTEM_GUIDE.md      # Detailed integration docs
├── README_INTEGRATED.md            # Integration overview
└── QUICK_START_INTEGRATED.md       # This file
```

## Next Steps

1. **Test Single Document**: Upload one RFP file to verify basic functionality
2. **Test Multi-Document**: Upload multiple files to test Phase 0 integration
3. **Review Results**: Check the analysis output and exports
4. **Customize**: Modify prompts and agents as needed

## Support

For detailed information:
- **Integration Details**: See [`INTEGRATED_SYSTEM_GUIDE.md`](INTEGRATED_SYSTEM_GUIDE.md)
- **Phase 0 Docs**: See [`document-consolidator/phase0_router/README.md`](document-consolidator/phase0_router/README.md)
- **RFP Analyzer Docs**: See [`rfp-analyzer/analyzer/README.md`](rfp-analyzer/analyzer/README.md)

## Summary

✅ **Single Document**: Works without Phase 0  
✅ **Multiple Documents**: Requires Phase 0 + ANTHROPIC_API_KEY  
✅ **Graceful Fallback**: Falls back to standard ingestion if Phase 0 unavailable  
✅ **Source Traceability**: Maintains document source information  
✅ **Conflict Detection**: Identifies contradictions across documents  