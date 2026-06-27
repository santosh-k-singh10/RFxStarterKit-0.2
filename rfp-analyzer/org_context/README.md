# Organizational Context Module

This module manages organizational context for the RFP Analyzer, supporting both local file-based configuration and dynamic loading from IBM ICA Context Studio via MCP.

## Overview

The organizational context includes:
- **Organization Configuration:** Tech stack, compliance requirements, naming conventions
- **Domain Knowledge:** Industry terminology, acronyms, technology glossaries
- **Standards:** Coding standards, security standards, compliance frameworks
- **Templates:** Document templates for proposals, technical specs, SOWs
- **Historical Data:** Past RFP responses and outcomes

## Architecture

```
org_context/
├── context_manager.py          # Central context manager
├── mcp_context_client.py       # MCP client for Context Studio
├── context_schema.py           # Pydantic models
├── context_studio_integration.py  # Legacy Context Studio integration
├── remote_loaders.py           # Remote file loaders
├── table_templates.py          # Table template definitions
├── config/                     # Configuration files
│   ├── org_config.yaml         # Local organization config
│   └── context_studio_config.example.yaml
├── domain_knowledge/           # Domain-specific knowledge
├── standards/                  # Organizational standards
├── templates/                  # Document templates
├── examples/                   # Example RFPs
├── schemas/                    # JSON-LD schemas for Context Studio
└── data/                       # JSON-LD data files for Context Studio
```

## Usage

### Option 1: Context Studio (Recommended)

Load context dynamically from IBM ICA Context Studio:

```python
from org_context.context_manager import initialize_context_manager

# Auto-detect from environment (CONTEXT_STUDIO_ENABLED=true)
cm = initialize_context_manager()

# Or explicitly enable
cm = initialize_context_manager(use_context_studio=True)

# Get context
context = cm.get_context()
print(f"Organization: {context.name}")
print(f"Tech Stack: {context.tech_stack.preferred_languages}")
```

**Benefits:**
- ✅ Automatic updates
- ✅ Semantic search
- ✅ Historical data access
- ✅ Domain knowledge
- ✅ Centralized management

### Option 2: Local Files

Load context from local YAML/JSON files:

```python
from org_context.context_manager import initialize_context_manager

# Load from local file
cm = initialize_context_manager("org_context/config/org_config.yaml")

context = cm.get_context()
```

### Option 3: Remote URLs

Load context from remote URLs (SharePoint, OneDrive, Box, HTTP):

```python
from org_context.context_manager import initialize_context_manager

# SharePoint
cm = initialize_context_manager(
    "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml",
    remote_kwargs={
        "client_id": "...",
        "client_secret": "...",
        "tenant_id": "..."
    }
)
```

## Context Studio Integration

### Setup

1. **Install dependencies:**
   ```bash
   pip install httpx structlog pyyaml
   ```

2. **Configure environment:**
   ```bash
   # .env file
   CONTEXT_STUDIO_ENABLED=true
   CONTEXT_STUDIO_MCP_URL=https://servicesessentials.ibm.com/mcp-gateway/...
   CONTEXT_STUDIO_MCP_TOKEN=your-token
   CONTEXT_STUDIO_API_KEY=your-key
   ```

3. **Use it:**
   ```python
   cm = initialize_context_manager()  # Auto-detects Context Studio
   ```

### Advanced Features

#### Semantic Search

```python
# Search across all context
results = cm.search_context(
    query="HIPAA compliance requirements",
    context_types=["standards", "domain_knowledge"],
    limit=5
)
```

#### Domain Knowledge

```python
# Get healthcare terminology
knowledge = cm.get_domain_knowledge(
    domain="healthcare",
    knowledge_type="all"
)

# Access terms
for term in knowledge['terms']:
    print(f"{term['term']}: {term['definition']}")
```

#### Historical RFPs

```python
# Get past successful RFPs
rfps = cm.get_historical_rfps(
    filters={
        "industry": "Retail",
        "outcome": "won",
        "years_back": 3
    },
    limit=10
)
```

## API Reference

### ContextManager

```python
class ContextManager:
    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        use_context_studio: bool = False,
        mcp_client: Optional[MCPContextClient] = None
    )
    
    def get_context(self) -> OrganizationContext
    def load_context(self, config_path: str | Path) -> OrganizationContext
    def reload_context(self) -> OrganizationContext
    def reload_from_context_studio(self) -> OrganizationContext
    
    def search_context(
        self,
        query: str,
        context_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]
    
    def get_domain_knowledge(
        self,
        domain: Optional[str] = None,
        knowledge_type: str = 'all'
    ) -> Dict[str, Any]
    
    def get_historical_rfps(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]
    
    def get_agent_context(self, agent_type: str) -> dict
    def get_prompt_context(self, agent_type: str) -> str
```

### MCPContextClient

```python
class MCPContextClient:
    def __init__(
        self,
        mcp_url: str,
        mcp_gateway_token: str,
        context_studio_key: str,
        cache_ttl: int = 300
    )
    
    def get_organization_context(
        self,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]
    
    def get_domain_knowledge(
        self,
        domain: Optional[str] = None,
        knowledge_type: str = 'all'
    ) -> Dict[str, Any]
    
    def get_standards_document(
        self,
        standard_type: str,
        standard_id: Optional[str] = None
    ) -> Dict[str, Any]
    
    def get_template(
        self,
        template_type: str,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]
    
    def get_historical_rfps(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]
    
    def search_context(
        self,
        query: str,
        context_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]
    
    def clear_cache(self)
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CONTEXT_STUDIO_ENABLED` | No | `false` | Enable Context Studio |
| `CONTEXT_STUDIO_MCP_URL` | Yes* | - | MCP gateway URL |
| `CONTEXT_STUDIO_MCP_TOKEN` | Yes* | - | MCP gateway token |
| `CONTEXT_STUDIO_API_KEY` | Yes* | - | Context Studio API key |
| `CONTEXT_STUDIO_CACHE_TTL` | No | `300` | Cache TTL (seconds) |
| `CONTEXT_STUDIO_CACHE_SIZE` | No | `100` | Max cached items |

*Required when `CONTEXT_STUDIO_ENABLED=true`

### Local Configuration

Edit `config/org_config.yaml`:

```yaml
name: "Your Organization"
industry: "Technology"
description: "Organization description"

tech_stack:
  preferred_languages:
    - Python
    - TypeScript
  cloud_providers:
    - AWS
    - Azure
  databases:
    - PostgreSQL
    - MongoDB

compliance:
  frameworks:
    - GDPR
    - SOC2
    - ISO 27001
  certifications:
    - ISO 9001
```

## Examples

See [`../examples/context_studio_example.py`](../examples/context_studio_example.py) for complete examples.

## Documentation

- **[Quick Start Guide](../CONTEXT_STUDIO_QUICKSTART.md)** - Get started in 5 minutes
- **[Integration Guide](../CONTEXT_STUDIO_INTEGRATION_GUIDE.md)** - Complete user guide
- **[Implementation Plan](../CONTEXT_STUDIO_MCP_IMPLEMENTATION_PLAN.md)** - Technical details
- **[Implementation Summary](../CONTEXT_STUDIO_IMPLEMENTATION_SUMMARY.md)** - What was built

## Troubleshooting

### "MCP URL not provided"

**Solution:** Set `CONTEXT_STUDIO_MCP_URL` in `.env`

### "Authentication failed"

**Solution:** Verify tokens are correct and not expired

### "Connection timeout"

**Solution:** Check internet connectivity and IBM ICA availability

For more help, see the [Integration Guide](../CONTEXT_STUDIO_INTEGRATION_GUIDE.md#troubleshooting).

## Migration from Local Files

1. **Backup local files:**
   ```bash
   cp -r org_context org_context.backup
   ```

2. **Import data to Context Studio:**
   - Use JSON-LD schemas in `schemas/`
   - Use JSON-LD data files in `data/`

3. **Enable Context Studio:**
   ```bash
   # .env
   CONTEXT_STUDIO_ENABLED=true
   ```

4. **Test:**
   ```bash
   python examples/context_studio_example.py
   ```

## Performance

- **Cache hit rate:** >80% (target)
- **API response time:** <200ms (p95)
- **Cache response time:** <1ms
- **Fallback:** Automatic to local files

## Support

For issues or questions:
1. Check documentation
2. Review example scripts
3. Check logs for errors
4. Contact IBM ICA support

---

**Module Version:** 2.0  
**Last Updated:** 2026-05-13  
**Maintainer:** IBM Bob