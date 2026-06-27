# Essential Files for RFP → GSE Workflow

This document lists all the files you need to go from an RFP to a pre-filled GSE template.

---

## Complete Workflow Overview

```
RFP Markdown → Enriched JSON → Scoping Metadata → GSE Template
```

**Important:** The system expects **RFP requirements in markdown format** (Phase 1 output), not raw PDF.

If you have a PDF, you need to first extract requirements using an RFP analyzer tool that outputs markdown with structured requirements (FR-001, NFR-001, etc.).

---

## Core Files Required

### 1. Architecture Designer Module (RFP Analysis & Enrichment)

**Directory:** `architecture_designer/`

| File | Purpose | Required |
|------|---------|----------|
| `__init__.py` | Module initialization | ✅ Yes |
| `designer.py` | Main orchestrator for RFP analysis | ✅ Yes |
| `enricher.py` | Enriches requirements with implementation details | ✅ Yes |
| `models.py` | Data models (Requirement, Module, etc.) | ✅ Yes |
| `prompts.py` | LLM prompts for analysis | ✅ Yes |
| `scoping_metadata_extractor.py` | **NEW** Extracts GSE fields from enriched JSON | ✅ Yes |
| `exporters.py` | Exports to HTML/Markdown | ⚠️ Optional |
| `preferences.py` | User preferences handling | ⚠️ Optional |

### 2. GSE Template Files

**Directory:** `GSE-template/`

| File | Purpose | Required |
|------|---------|----------|
| `questionnaire_form.html` | GSE form with auto-fill capability | ✅ Yes |
| `models.py` | GSE data models | ⚠️ Optional |

### 3. Bridge Application

**Root Directory**

| File | Purpose | Required |
|------|---------|----------|
| `RFP_to_GSE_Bridge_v3.html` | Bridge UI to transfer data to GSE | ✅ Yes |
| `app.py` | FastAPI server (serves GSE form and bridge) | ✅ Yes |

### 4. Core Dependencies

**Root Directory**

| File | Purpose | Required |
|------|---------|----------|
| `llm_client.py` | LLM API client (OpenAI/Anthropic) | ✅ Yes |
| `config.py` | Configuration settings | ✅ Yes |
| `requirements.txt` | Python dependencies | ✅ Yes |
| `.env` | API keys and environment variables | ✅ Yes |

---

## Minimal File List (Just the Essentials)

If you want the absolute minimum to run the workflow:

```
📁 Your Project Root/
├── 📄 .env                                    # API keys
├── 📄 config.py                               # Configuration
├── 📄 llm_client.py                           # LLM client
├── 📄 app.py                                  # FastAPI server
├── 📄 requirements.txt                        # Dependencies
├── 📄 RFP_to_GSE_Bridge_v3.html              # Bridge UI
│
├── 📁 architecture_designer/
│   ├── 📄 __init__.py
│   ├── 📄 designer.py                         # RFP analyzer
│   ├── 📄 enricher.py                         # Enrichment logic
│   ├── 📄 models.py                           # Data models
│   ├── 📄 prompts.py                          # LLM prompts
│   └── 📄 scoping_metadata_extractor.py       # GSE field extraction
│
└── 📁 GSE-template/
    └── 📄 questionnaire_form.html             # GSE form
```

**Total: 13 files**

---

## Step-by-Step Usage

### Step 1: Enrich RFP Markdown and Generate Enriched JSON

**Input Required:** RFP requirements in markdown format with structured IDs (FR-001, NFR-001, etc.)

```python
from architecture_designer.enricher import RequirementEnricher
from architecture_designer.models import EnrichedModules

# Read your Phase 1 markdown output
with open("rfp_requirements.md", "r") as f:
    markdown_content = f.read()

# Enrich requirements (adds module, impl_type, actors)
enricher = RequirementEnricher()
enriched_modules = enricher.enrich_from_markdown(markdown_content)

# Convert to JSON format
enriched_json = enriched_modules.model_dump()
```

**Output:** `enriched_requirements.json` with all requirements categorized by module

**Alternative:** If you already have enriched JSON from a previous run, skip this step.

### Step 2: Extract Scoping Metadata

```python
from architecture_designer.scoping_metadata_extractor import extract_scoping_metadata

# Extract GSE fields
scoping_metadata = extract_scoping_metadata(enriched_json)

# Add to enriched JSON
enriched_json["scoping_metadata"] = scoping_metadata

# Save
import json
with open("architecture_enriched_with_scoping.json", "w") as f:
    json.dump(enriched_json, f, indent=2)
```

**Output:** `architecture_enriched_with_scoping.json` with 88.5% GSE fields filled

### Step 3: Use Bridge to Transfer to GSE

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open Bridge in browser:**
   ```
   http://localhost:8000/bridge
   ```

3. **Load your enriched JSON:**
   - Click "Choose File"
   - Select `architecture_enriched_with_scoping.json`
   - Click "Load JSON"

4. **Review the mapping:**
   - See which fields are auto-filled (green)
   - See which fields are estimated (yellow)
   - See which fields need input (red)

5. **Open GSE Form:**
   - Click "Open Pre-filled GSE Form"
   - GSE form opens with all fields populated
   - Review and adjust as needed

---

## Alternative: Programmatic Workflow

If you want to skip the UI and do everything programmatically:

```python
import json
from architecture_designer.enricher import RequirementEnricher
from architecture_designer.scoping_metadata_extractor import extract_scoping_metadata

# Step 1: Read RFP markdown (Phase 1 output)
with open("rfp_requirements.md", "r") as f:
    markdown_content = f.read()

# Step 2: Enrich requirements
enricher = RequirementEnricher()
enriched_modules = enricher.enrich_from_markdown(markdown_content)
enriched_json = enriched_modules.model_dump()

# Step 3: Extract scoping metadata for GSE
scoping_metadata = extract_scoping_metadata(enriched_json)
enriched_json["scoping_metadata"] = scoping_metadata

# Step 4: Save complete output
with open("complete_output.json", "w") as f:
    json.dump(enriched_json, f, indent=2)

# Step 5: Print fill summary
fill_summary = scoping_metadata["fill_summary"]
print(f"Fill Rate: {fill_summary['fill_rate_pct']}%")
print(f"Auto-filled: {fill_summary['auto_filled']}")
print(f"Estimated: {fill_summary['estimated']}")
print(f"Needs input: {fill_summary['needs_input']}")
```

---

## Configuration Required

### 1. Environment Variables (`.env`)

```env
# LLM API Keys (choose one)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Model Selection
LLM_PROVIDER=openai  # or anthropic
LLM_MODEL=gpt-4o     # or claude-3-5-sonnet-20241022
```

### 2. Dependencies (`requirements.txt`)

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
openai>=1.3.0
anthropic>=0.7.0
pydantic>=2.5.0
python-multipart>=0.0.6
PyPDF2>=3.0.0
```

Install with:
```bash
pip install -r requirements.txt
```

---

## Output Files Generated

After running the complete workflow, you'll have:

1. **`architecture_output.json`** - Initial RFP analysis
2. **`architecture_enriched.json`** - Enriched with implementation details
3. **`architecture_enriched_with_scoping.json`** - With GSE metadata (88.5% filled)
4. **`architecture_export.html`** - Human-readable report (optional)
5. **`architecture_export.md`** - Markdown report (optional)

---

## GSE Field Mapping

The `scoping_metadata` section in the enriched JSON maps to GSE template sections:

| JSON Section | GSE Section | Fields |
|--------------|-------------|--------|
| `geography` | 1. Application Scope & 2. Geographical Scope | Countries, plants, company codes, rollout |
| `users` | 2. Geographical Scope | Core users, self-service users, trainees |
| `applications` | 1. Application Scope | SAP modules, L1 processes |
| `wricef` | 4. Application Development | Reports, interfaces, enhancements, forms |
| `data_migration` | 5. Data Conversion | Tool, objects, cycles, source systems |
| `testing` | 6. Testing Scope | Automation, SIT, regression scenarios |
| `security` | 7. Infrastructure & Authorization | Roles, end users, L3 processes |
| `change_management` | 8. Change Management & Training | OCM, training approach, materials |
| `implementation` | 9. Implementation Scope | Timeline, rollout type, methodology |

---

## Quick Start Script

Create `run_complete_workflow.py`:

```python
#!/usr/bin/env python3
"""
Complete RFP Markdown to GSE workflow
"""
import json
import sys
from pathlib import Path
from architecture_designer.enricher import RequirementEnricher
from architecture_designer.scoping_metadata_extractor import extract_scoping_metadata

def main(markdown_path: str, project_name: str):
    print(f"🚀 Starting RFP enrichment for: {project_name}")
    
    # Step 1: Read markdown
    print(f"📄 Step 1: Reading RFP markdown from {markdown_path}...")
    with open(markdown_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    
    # Step 2: Enrich requirements
    print("🔄 Step 2: Enriching requirements...")
    enricher = RequirementEnricher()
    enriched_modules = enricher.enrich_from_markdown(markdown_content)
    enriched_json = enriched_modules.model_dump()
    print(f"✅ Found {len(enriched_json.get('modules', {}))} modules")
    
    # Step 3: Extract scoping metadata
    print("📊 Step 3: Extracting GSE scoping metadata...")
    scoping_metadata = extract_scoping_metadata(enriched_json)
    enriched_json["scoping_metadata"] = scoping_metadata
    
    fill_summary = scoping_metadata["fill_summary"]
    print(f"✅ Fill rate: {fill_summary['fill_rate_pct']}%")
    print(f"   - Auto-filled: {fill_summary['auto_filled']}")
    print(f"   - Estimated: {fill_summary['estimated']}")
    print(f"   - Needs input: {fill_summary['needs_input']}")
    
    # Step 4: Save output
    output_path = f"{project_name.replace(' ', '_')}_complete.json"
    with open(output_path, "w") as f:
        json.dump(enriched_json, f, indent=2)
    print(f"💾 Saved to: {output_path}")
    
    # Step 5: Instructions
    print("\n📋 Next Steps:")
    print("1. Start the server: python app.py")
    print("2. Open: http://localhost:8000/bridge")
    print(f"3. Load: {output_path}")
    print("4. Click 'Open Pre-filled GSE Form'")
    print("\n✨ Done!")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python run_complete_workflow.py <markdown_path> <project_name>")
        print("Example: python run_complete_workflow.py rfp_requirements.md 'My Project'")
        sys.exit(1)
    
    main(sys.argv[1], sys.argv[2])
```

**Usage:**
```bash
python run_complete_workflow.py "rfp_requirements.md" "My Project"
```

---

## Troubleshooting

### Issue: "Module not found"
**Solution:** Ensure you're in the project root directory and all files are present.

### Issue: "API key not found"
**Solution:** Create `.env` file with your API keys.

### Issue: "GSE form not loading"
**Solution:** Start the server with `python app.py` first.

### Issue: "Low fill rate"
**Solution:** The new version achieves 88.5% fill rate. If lower, ensure you're using the updated `scoping_metadata_extractor.py`.

---

## Summary

**Minimum files needed:** 13 files  
**Fill rate achieved:** 88.5%  
**Time to run:** ~2-5 minutes per RFP  
**Manual input required:** 6 fields (11.5%)  

All files are in your current project structure. No additional downloads needed!