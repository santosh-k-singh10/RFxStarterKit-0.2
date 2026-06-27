# SAP Requirements Mapping Analyzer

**Standalone Tool for SAP-Specific RFP Analysis**

This is a separate, independent tool that processes RFP Analyzer output and maps requirements to SAP modules. It runs completely independently from the main RFP analyzer and is designed specifically for SAP RFPs.

## Overview

The SAP Mapping Analyzer takes requirements (from any source) and:
- Maps them to appropriate SAP modules (FI, CO, MM, SD, PP, etc.)
- Calculates coverage percentage
- Identifies gaps requiring custom development
- Provides implementation recommendations

## Architecture

```
Main RFP Analyzer → Outputs (JSON/MD/Excel)
         ↓
  [Copy/Paste or Upload]
         ↓
SAP Mapping Analyzer → SAP Module Analysis
```

## Installation

The SAP Analyzer uses the same dependencies as the main RFP analyzer:

```bash
cd rfp-analyzer
pip install -r requirements.txt
```

## Usage

### Option 1: Web Interface (Recommended)

Start the web server:

```bash
python sap_analyzer_app.py
```

Then open your browser to: **http://localhost:8002**

Features:
- Paste requirements directly
- Upload RFP Analyzer JSON output
- Interactive results visualization
- Export results as JSON

### Option 2: Command Line Interface

#### Analyze from text file:

```bash
python sap_analyzer_cli.py analyze requirements.txt
```

#### Analyze from RFP Analyzer JSON:

```bash
python sap_analyzer_cli.py analyze-json outputs/rfp_analysis.json
```

#### Interactive mode:

```bash
python sap_analyzer_cli.py interactive
```

#### With output file:

```bash
python sap_analyzer_cli.py analyze requirements.txt --output sap_mapping.json
```

#### Different output formats:

```bash
# Summary (default)
python sap_analyzer_cli.py analyze requirements.txt

# JSON output
python sap_analyzer_cli.py analyze requirements.txt --format json

# Markdown output
python sap_analyzer_cli.py analyze requirements.txt --format markdown
```

## Workflow Examples

### Workflow 1: From Main RFP Analyzer

1. Run main RFP analyzer:
   ```bash
   python main.py analyze rfp.pdf
   ```

2. This generates: `outputs/rfp_analysis.json`

3. Feed to SAP analyzer:
   ```bash
   python sap_analyzer_cli.py analyze-json outputs/rfp_analysis.json
   ```

4. Get SAP-specific analysis with module mapping!

### Workflow 2: Quick Analysis

1. Copy functional requirements from RFP analyzer output

2. Open SAP analyzer web UI:
   ```bash
   python sap_analyzer_app.py
   ```

3. Paste requirements and click "Analyze"

4. View SAP module breakdown instantly

### Workflow 3: Batch Processing

Create a text file with requirements:

```text
# requirements.txt
The system shall manage accounts payable
The system shall support general ledger accounting
The system shall handle purchase order creation
The system shall manage sales orders with pricing
```

Then analyze:

```bash
python sap_analyzer_cli.py analyze requirements.txt --output sap_analysis.json
```

## Input Formats

### Text File (one requirement per line)
```text
The system shall manage accounts payable including invoice processing
The system shall support general ledger accounting with real-time postings
The system shall handle purchase order creation and goods receipt
```

### RFP Analyzer JSON
```json
{
  "requirements": [
    {
      "id": "FR-001",
      "description": "The system shall manage accounts payable",
      "category": "functional"
    }
  ]
}
```

### Direct Paste (Web UI)
Just paste requirements, one per line, into the web interface.

## Output

### Summary Format (CLI)
```
Coverage Analysis
─────────────────
Total Requirements:  10
Mapped to SAP:       8
Coverage:            80%

Identified SAP Modules
──────────────────────────
Module    Requirements
FI        3
MM        2
SD        2
CO        1

Recommendations
───────────────
1. Implement SAP FI for financial accounting
2. Deploy MM module for procurement
3. Plan for integration between 4 SAP modules
```

### JSON Format
```json
{
  "mapped_modules": {
    "FI": ["req1", "req2"],
    "MM": ["req3"]
  },
  "coverage_analysis": {
    "total_requirements": 10,
    "mapped_requirements": 8,
    "coverage_percentage": 80.0
  },
  "recommendations": [...],
  "gaps": {
    "unmapped_requirements": [...],
    "custom_development_needed": true
  }
}
```

## SAP Modules Supported

The analyzer recognizes these SAP modules:

| Code | Module Name | Keywords |
|------|-------------|----------|
| FI | Financial Accounting | financial, accounting, GL, AP, AR |
| CO | Controlling | controlling, cost center, profit center |
| MM | Materials Management | procurement, purchasing, inventory |
| SD | Sales & Distribution | sales, orders, pricing, delivery |
| PP | Production Planning | manufacturing, production, MRP |
| QM | Quality Management | quality, inspection, control |
| PM | Plant Maintenance | maintenance, equipment, work orders |
| HR/HCM | Human Capital Mgmt | HR, payroll, personnel, time |
| WM | Warehouse Management | warehouse, storage, bins |
| PS | Project System | projects, WBS |
| BW/BI | Business Warehouse | reporting, analytics, BI |
| CRM | Customer Relationship | CRM, customer, marketing |
| SRM | Supplier Relationship | SRM, vendor, sourcing |
| SCM | Supply Chain Mgmt | supply chain, planning, logistics |

## Integration with Main Analyzer

### As a Separate Tab (Future Enhancement)

You can add the SAP analyzer as a tab in your main web interface:

```python
# In web_app.py - add SAP tab
@app.get("/sap-analyzer")
async def sap_analyzer_page():
    # Redirect to standalone SAP analyzer
    return RedirectResponse(url="http://localhost:8002")
```

## API Endpoints

The web application exposes these endpoints:

### POST /api/analyze
Analyze requirements from JSON array.

**Request:**
```json
{
  "requirements": [
    "The system shall manage accounts payable",
    "The system shall support purchase orders"
  ]
}
```

**Response:** SAP analysis JSON

### POST /api/analyze-file
Upload and analyze file (JSON or Markdown).

### GET /api/health
Health check endpoint.

## Files

- `sap_analyzer_app.py` - Web application (FastAPI)
- `sap_analyzer_cli.py` - Command-line interface
- `agents/sap_mapping_agent.py` - Core SAP mapping logic
- `examples/sap_mapping_example.py` - Usage examples
- `SAP_ANALYZER_README.md` - This file

## Benefits

✅ **Standalone** - Runs independently from main analyzer  
✅ **Flexible** - Works with any requirement source  
✅ **SAP-Specific** - Specialized for SAP RFPs only  
✅ **Multiple Interfaces** - Web UI, CLI, and programmatic  
✅ **Easy Integration** - Processes main analyzer output  

## Troubleshooting

### Port Already in Use
If port 8002 is busy:
```bash
python sap_analyzer_app.py --port 8003
```

### Import Errors
Ensure you're in the rfp-analyzer directory:
```bash
cd rfp-analyzer
python sap_analyzer_app.py
```

### No Results
Check that requirements contain SAP-relevant keywords (financial, procurement, sales, etc.)

## Examples

See `examples/sap_mapping_example.py` for comprehensive examples including:
- Basic SAP module mapping
- Integration with RFP Analyzer
- Gap analysis
- Export for proposals

Run examples:
```bash
python examples/sap_mapping_example.py
```

## License

Same as main RFP Analyzer project.
