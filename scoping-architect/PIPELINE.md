# RFP Analyzer — Full Pipeline Integration Guide

Complete guide for connecting Phase 1 → Phase 1.5 → Phase 2.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 1 — Requirement Extraction                                    │
│  Tool: your extractor                                                │
│  Input:  raw RFP document (PDF / Word / text)                       │
│  Output: requirements.md                                             │
│          FR-001...FR-N, NFR-001...NFR-N, CR-001...CR-N,             │
│          AMB-001...AMB-N, RISK-001...RISK-N                         │
│          Each with: priority (MoSCoW), confidence %, related IDs     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  requirements.md
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 1.5 — Requirement Enrichment (AUTOMATIC)                      │
│  Tool: RequirementEnricher (built-in)                               │
│  Input:  requirements.md (markdown text)                            │
│  Output: EnrichedModules object                                      │
│          Each requirement gains:                                      │
│            module     — identity_access | cart_checkout | …          │
│            impl_type  — custom_build | third_party_integration | …   │
│            actors     — customer | admin | guest | system            │
│            dependency_direction — depends_on | depended_by | …       │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  EnrichedModules
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Phase 2 — Architecture Generation                                   │
│  Tool: ArchitectureDesigner                                          │
│  Input:  EnrichedModules + user preferences                         │
│  Output: ArchitectureOutput                                          │
│          ├── System context (actors, integrations, boundary)         │
│          ├── Architecture pattern + rationale                        │
│          ├── Components with module, impl_type, actors               │
│          │   story_point_range, source_requirements                  │
│          └── Risk register with module attribution                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Option A — Python Script (Recommended for automation)

```python
from architecture_designer import ArchitectureDesigner, DeploymentTarget
from architecture_designer.enricher import RequirementEnricher
from architecture_designer.exporters import MarkdownExporter, JsonExporter
import asyncio

async def main():
    # Load requirements markdown
    with open("requirements.md", "r") as f:
        requirements_md = f.read()
    
    # Phase 1.5: Auto-enrich requirements
    enricher = RequirementEnricher()
    enriched = await enricher.enrich_markdown(requirements_md)
    
    # Phase 2: Generate architecture
    designer = ArchitectureDesigner(max_tokens=8000)
    result = await designer.analyze_enriched_async(
        enriched,
        project_name="ABC E-commerce Platform",
        deployment_target=DeploymentTarget.CLOUD,
        domain_context="ecommerce",
        extra_constraints=[
            "Cloud provider: AWS",
            "Compliance: PCI DSS, GDPR",
            "Timeline: 6-month phased delivery",
        ],
    )
    
    # Export results
    md_exporter = MarkdownExporter()
    json_exporter = JsonExporter()
    
    with open("architecture.md", "w") as f:
        f.write(md_exporter.export(result))
    
    with open("architecture.json", "w") as f:
        f.write(json_exporter.export(result))
    
    print(f"✅ Architecture generated: {result.summary.component_count} components")
    print(f"   Story points: {result.total_story_points}")

asyncio.run(main())
```

### Option B — FastAPI Web Interface (Recommended for interactive use)

#### 1. Start the server

```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or set OPENAI_API_BASE, OPENAI_API_KEY, MODEL_ID for IBM Services Essentials

python run.py
# Server starts at http://localhost:8000
```

#### 2. Use the web interface

Open http://localhost:8000 in your browser:
1. Fill out the 3-step preferences form
2. Upload your requirements markdown file
3. Click "Generate architecture"
4. View results with metrics, components, and risks

#### 3. Or use the API directly

```bash
# Step 1: Submit preferences (optional)
curl -X POST http://localhost:8000/api/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "approach": "greenfield",
    "deployment": "cloud",
    "cloud": "aws",
    "compliance": ["pci", "gdpr"],
    "channels": ["web", "mobile_native"],
    "integration": "rest",
    "timeline": "phased"
  }'

# Step 2: Generate architecture (auto-enriches requirements)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "ABC E-commerce Platform",
    "requirements": "# Requirements\n\n## FR-001: User Login\n...",
    "preferences": {
      "approach": "greenfield",
      "deployment": "cloud",
      "cloud": "aws",
      "compliance": ["pci", "gdpr"]
    }
  }' > architecture.json

# Step 3: Export as Markdown
curl -X POST http://localhost:8000/api/export/markdown \
  -H "Content-Type: application/json" \
  -d @architecture.json > architecture.md
```

### Option C — Example Script

```bash
# Mock mode (no API key needed)
python example_usage.py --mock

# With API key
export ANTHROPIC_API_KEY=sk-ant-...
python example_usage.py

# With requirements file
python example_usage.py --requirements requirements.md

# Legacy flat path
python example_usage.py --flat
```

---

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface with 3-step wizard |
| `/api/health` | GET | Health check |
| `/api/preferences` | POST | Validate and structure preferences |
| `/api/analyze` | POST | Full pipeline with auto-enrichment |
| `/api/analyze/enriched` | POST | Direct enriched analysis |
| `/api/export/markdown` | POST | Export as Markdown document |
| `/api/export/json` | POST | Export as formatted JSON |
| `/docs` | GET | Swagger UI documentation |
| `/redoc` | GET | ReDoc documentation |

### Request/Response Examples

#### POST /api/analyze

**Request:**
```json
{
  "project_name": "ABC E-commerce Platform",
  "requirements": "# Requirements\n\n## FR-001: User Login\nSecure login with email/password...",
  "preferences": {
    "approach": "greenfield",
    "deployment": "cloud",
    "cloud": "aws",
    "compliance": ["pci", "gdpr"],
    "channels": ["web"],
    "integration": "rest",
    "timeline": "phased"
  }
}
```

**Response:**
```json
{
  "project_name": "ABC E-commerce Platform",
  "deployment_target": "cloud",
  "is_enriched": true,
  "summary": {
    "component_count": 12,
    "total_story_points_mid": 87,
    "story_points": { "low": 55, "mid": 87, "high": 134 },
    "compliance_components": 3,
    "open_ambiguities": 2,
    "avg_complexity": "Medium"
  },
  "architecture": {
    "recommended": "Modular Monolith with API-first layer",
    "rationale": "...",
    "key_principles": ["API-first", "Compliance by design"],
    "domain_note": "PCI DSS applies to payment components"
  },
  "components": [
    {
      "name": "Auth Service",
      "type": "Backend Service",
      "module": "identity_access",
      "impl_type": "custom_build",
      "actors": ["customer", "guest"],
      "complexity": "Medium",
      "story_point_range": { "low": 5, "mid": 8, "high": 13 },
      "source_requirements": ["FR-001", "FR-002"],
      "compliance_impacted": false
    }
  ],
  "risks": [
    {
      "risk": "PCI scope underestimated",
      "level": "High",
      "mitigation": "Use Stripe Elements to keep card data off servers",
      "module": "cart_checkout"
    }
  ]
}
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key for Claude |
| `OPENAI_API_BASE` | Yes* | IBM Services Essentials base URL |
| `OPENAI_API_KEY` | Yes* | IBM Services Essentials API key |
| `MODEL_ID` | Yes* | Model ID for IBM Services Essentials |
| `CORS_ORIGINS` | No | Comma-separated allowed origins (default: `*`) |

*Either Anthropic OR IBM Services Essentials credentials required

---

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=architecture_designer --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests with specific marker
pytest -m "not slow"

# Run in verbose mode
pytest -v
```

---

## Project Structure

```
c:/Agents/scoping-architect/
├── app.py                          # FastAPI application with web UI
├── run.py                          # Server startup script
├── router.py                       # API endpoints
├── schemas.py                      # Pydantic request/response models
├── llm_client.py                   # LLM client (Anthropic + IBM)
├── config.py                       # Configuration management
├── example_usage.py                # Usage examples
├── PIPELINE.md                     # This file
├── README.md                       # Project overview
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
│
├── architecture_designer/          # Core module
│   ├── __init__.py                # Module exports
│   ├── designer.py                # ArchitectureDesigner class
│   ├── models.py                  # Data models
│   ├── preferences.py             # User preferences
│   ├── prompts.py                 # LLM prompts
│   ├── enricher.py                # Auto-enrichment (Phase 1.5)
│   └── exporters.py               # Markdown/JSON exporters
│
└── tests/                          # Test suite
    ├── conftest.py                # Pytest fixtures
    ├── test_models.py             # Model tests
    └── README.md                  # Test documentation
```

---

## Workflow Examples

### Example 1: Simple Analysis

```python
import asyncio
from architecture_designer import ArchitectureDesigner
from architecture_designer.enricher import RequirementEnricher

async def simple_analysis():
    requirements = """
    # Requirements
    ## FR-001: User Login
    Secure login with email/password
    
    ## FR-002: Product Catalog
    Browse and search products
    """
    
    enricher = RequirementEnricher()
    enriched = await enricher.enrich_markdown(requirements)
    
    designer = ArchitectureDesigner()
    result = await designer.analyze_enriched_async(enriched)
    
    print(f"Components: {result.summary.component_count}")
    print(f"Story points: {result.total_story_points['mid']}")

asyncio.run(simple_analysis())
```

### Example 2: With Preferences

```python
from architecture_designer.preferences import (
    PreferencesCollector, BuildApproach, CloudProvider
)

prefs_data = {
    "approach": "greenfield",
    "deployment": "cloud",
    "cloud": "aws",
    "compliance": ["pci", "gdpr"]
}

prefs = PreferencesCollector.from_dict(prefs_data)
arch_input = prefs.to_architecture_input(
    requirements=requirements_md,
    project_name="My Project"
)

result = ArchitectureDesigner().analyze(arch_input)
```

### Example 3: Export Results

```python
from architecture_designer.exporters import MarkdownExporter, JsonExporter

# After getting result from analysis
md_exporter = MarkdownExporter()
json_exporter = JsonExporter()

# Export as Markdown
markdown_doc = md_exporter.export(result)
with open("architecture.md", "w") as f:
    f.write(markdown_doc)

# Export as JSON
json_doc = json_exporter.export(result, indent=2)
with open("architecture.json", "w") as f:
    f.write(json_doc)
```

---

## Troubleshooting

### Issue: "No LLM provider is configured"

**Solution:** Set either:
- `ANTHROPIC_API_KEY` for Claude, OR
- `OPENAI_API_BASE`, `OPENAI_API_KEY`, and `MODEL_ID` for IBM Services Essentials

### Issue: JSON truncation errors

**Solution:** The system now uses 8000 tokens by default and includes automatic JSON repair. If issues persist, check the logs for details.

### Issue: Import errors

**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Tests failing

**Solution:** Tests don't require API keys. Run with:
```bash
pytest -v
```

---

## Best Practices

1. **Always use auto-enrichment**: The `/api/analyze` endpoint automatically enriches requirements for better results

2. **Provide domain context**: Include `domain_context` (e.g., "ecommerce", "healthcare") for more accurate architecture

3. **Specify constraints**: Use `extra_constraints` to provide cloud provider, compliance, timeline info

4. **Review ambiguities**: Check `summary.open_ambiguities` and address unclear requirements

5. **Export results**: Use the export endpoints to save architecture documents

6. **Monitor logs**: Check terminal output for detailed pipeline execution logs

---

## Next Steps

1. **Customize prompts**: Edit `architecture_designer/prompts.py` for domain-specific guidance

2. **Add modules**: Extend `EnrichedModules.MODULE_LABELS` for new functional areas

3. **Integrate with CI/CD**: Use the Python API in automated pipelines

4. **Build custom UI**: Use the API endpoints to create custom interfaces

---

## Support

- **Documentation**: See README.md and inline code documentation
- **API Docs**: http://localhost:8000/docs (when server is running)
- **Examples**: See example_usage.py for comprehensive examples
- **Tests**: See tests/ directory for usage patterns