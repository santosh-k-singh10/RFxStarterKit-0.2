# Automatic Requirement Enrichment

## Overview

The `/api/analyze` endpoint now **automatically enriches** Phase 1 markdown requirements before generating architecture. This means you no longer need to use the separate `rfp_requirement_enricher.html` tool - enrichment happens server-side!

## What is Enrichment?

Enrichment adds critical metadata to each requirement:

1. **Module** - Which functional area (identity_access, product_catalog, cart_checkout, etc.)
2. **Implementation Type** - How to build it (custom_build, third_party_integration, configuration, etc.)
3. **Actors** - Who it serves (customer, admin, guest, system, all)
4. **Dependencies** - Relationships between requirements

This enriched data enables:
- ✅ Better component boundaries
- ✅ Story point estimates (low/mid/high)
- ✅ Requirement traceability
- ✅ More accurate architecture recommendations

## How It Works

### Before (Manual Process)
```
Phase 1 Markdown
    ↓
rfp_requirement_enricher.html (manual step)
    ↓
rfp_enriched_requirements.json
    ↓
POST /api/analyze/enriched
    ↓
Architecture Output
```

### Now (Automatic)
```
Phase 1 Markdown
    ↓
POST /api/analyze (auto-enriches internally)
    ↓
Architecture Output with story points & traceability
```

## Usage

### Web UI
1. Open `http://localhost:8000`
2. Fill preferences form
3. Upload Phase 1 markdown file
4. **Architecture is automatically generated with enrichment!**

### API Call
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "approach": "greenfield",
      "deployment": "cloud",
      "cloud": "aws"
    },
    "requirements": "### FR-001 — User Login\nUsers must be able to login...",
    "project_name": "My Project"
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "preferences": {
            "approach": "greenfield",
            "deployment": "cloud",
            "cloud": "aws"
        },
        "requirements": """
### FR-001 — User Authentication
Users must be able to register and login using email and password.

**Priority:** MUST
**Confidence:** 95%

### FR-002 — Product Catalog
System must display a searchable product catalog.

**Priority:** MUST
**Confidence:** 90%
        """,
        "project_name": "E-Commerce Platform"
    }
)

architecture = response.json()
print(f"Components: {architecture['summary']['component_count']}")
print(f"Story Points: {architecture['summary']['total_story_points_mid']}")
```

## Logging Output

The enrichment process is fully logged:

```
======================================================================
POST /api/analyze - Starting architecture analysis with auto-enrichment
======================================================================
Project: E-Commerce Platform
Requirements length: 536 characters
Building preferences from request...
  - Deployment target: DeploymentTarget.CLOUD
  - Domain context: None
Auto-enriching requirements (Phase 1.5)...
======================================================================
Starting automatic requirement enrichment
======================================================================
Parsing markdown requirements...
  - Parsed 5 requirements
  - Types: FR=3, NFR=2, CR=0, AMB=0, RISK=0
Enriching requirements with LLM...
  - Batch 1: 5 FR/NFR requirements
  - Batch 2: 0 CR/AMB/RISK requirements
Calling LLM for enrichment (2 batches)...
  - Enriched 5 requirements
Inferring dependency directions...
  - Processing 2 dependency pairs
  - Applied 2 dependency directions
✓ Enrichment complete
  - Total requirements: 5
  - Modules: 3
  - Module breakdown:
    • Identity & access: 1 requirements
    • Product catalog: 2 requirements
    • Cart & checkout: 2 requirements
======================================================================
✓ Requirements enriched: 5 requirements in 3 modules
Initializing ArchitectureDesigner for enriched analysis...
Starting enriched async architecture analysis...
...
✓ Architecture analysis completed successfully
  - Components generated: 8
  - Domains identified: 3
  - Risks identified: 2
  - Total story points (mid): 89
======================================================================
```

## Module Mapping Rules

The enricher uses these rules to classify requirements:

### Modules
- **identity_access**: authentication, login, registration, RBAC, password, sessions
- **product_catalog**: products, search, filtering, categories, SKUs, inventory
- **cart_checkout**: cart, orders, payments, checkout flow, order tracking
- **content_management**: blog, admin dashboard, CMS, image gallery, SEO
- **integrations**: third-party services (analytics, CRM, email, social auth)
- **compliance_privacy**: GDPR, CCPA, PCI DSS, cookie consent, SSL, WCAG
- **platform_nfr**: performance, uptime, scalability, hosting, backups

### Implementation Types
- **custom_build**: Logic written from scratch (auth flows, business logic, UI)
- **third_party_integration**: External API/service (Stripe, SendGrid, Analytics)
- **configuration**: Infrastructure setup (SSL cert, hosting, analytics tag)
- **compliance_control**: Legal requirement (GDPR consent, PCI tokenization)
- **not_applicable**: Ambiguities, risks, meta-requirements

### Actors
- **customer**: End users browsing, buying, managing accounts
- **admin**: Staff managing content, orders, products
- **guest**: Unauthenticated users
- **system**: Automated/background processes (email, backups, analytics)
- **all**: Applies to everyone (accessibility, performance)

## Benefits

### 1. Story Point Estimates
Each component gets a range:
```json
{
  "name": "User Service",
  "story_point_range": {
    "low": 8,
    "mid": 13,
    "high": 21
  }
}
```

### 2. Requirement Traceability
Components are linked to source requirements:
```json
{
  "name": "Authentication Service",
  "source_requirements": ["FR-001", "FR-002", "NFR-008"]
}
```

### 3. Better Architecture
Module groupings guide component boundaries and help the LLM understand the system structure.

### 4. Implementation Guidance
Knowing if something is custom_build vs third_party_integration helps with:
- Technology selection
- Effort estimation
- Risk assessment

## Manual Enrichment (Still Available)

If you prefer manual control, you can still use:

1. **Standalone tool**: `rfp_requirement_enricher.html`
2. **Enriched endpoint**: `POST /api/analyze/enriched`

But for most use cases, the automatic enrichment in `/api/analyze` is recommended!

## Performance

Enrichment adds approximately:
- **2-3 LLM calls** (enrichment batches + dependency inference)
- **30-60 seconds** processing time
- **~10,000 tokens** usage (depending on requirement count)

The benefits far outweigh the cost for production architecture generation.

## Error Handling

If enrichment fails:
- The error is logged with full details
- The request returns a 500 error with the failure reason
- Check the server logs for debugging information

Common issues:
- Invalid markdown format (requirements must be `### FR-001 — Title`)
- LLM API errors (check API key and connectivity)
- Token limits exceeded (reduce requirement count)

## Disabling Auto-Enrichment

If you need to disable auto-enrichment (not recommended), you would need to:
1. Modify `router.py` to skip the enrichment step
2. Use the legacy flat requirements path

However, this loses story points, traceability, and architecture quality.