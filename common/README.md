# Common Configuration Files

This directory contains shared configuration templates and base dependencies used across all modules in the RFxStarterKit project.

## Files

### `.env.template`
Master environment configuration template containing all possible environment variables used across different modules.

**Usage:**
1. Copy this file to `.env` in your module directory
2. Fill in the values relevant to your module
3. Different modules use different subsets of these variables

**Key Sections:**
- **LLM Provider Configuration** - IBM Services Essentials, Anthropic, or AWS Bedrock
- **Server Configuration** - Port, CORS, A2A protocol
- **ICA Integration** - Agent Studio integration
- **MCP Gateway** - IBM ICA MCP Gateway configuration
- **Context Studio** - Context Studio integration (RFP Analyzer)
- **Observability** - Arize Phoenix observability (RFP Analyzer)
- **Authentication** - Bearer token or Keycloak JWT
- **Logging & Debug** - Optional logging and debug settings

### `requirements-base.txt`
Base Python dependencies shared across all modules.

**Includes:**
- `anthropic` - Core AI/LLM library
- `fastapi` - API framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration
- `httpx` - HTTP client
- `pytest` - Testing framework

**Usage:**
```bash
# Install base dependencies
pip install -r common/requirements-base.txt

# Then install module-specific dependencies
pip install -r <module>/requirements.txt
```

## Module-Specific Configurations

### Scoping Architect Module
**Location:** `scoping-architect/.env`

**Required Variables:**
- `OPENAI_API_BASE`
- `OPENAI_API_KEY`
- `MODEL_ID`
- `MCP_BASE_URL`
- `MCP_SERVER_ID`
- `MCP_ACCESS_TOKEN`

**Additional Dependencies:**
None - uses only base dependencies

### RFP Analyzer Module (Root)
**Location:** `rfp-analyzer/.env`

**Required Variables:**
Same as Architecture module

### RFP Analyzer Module (Application)
**Location:** `rfp-analyzer/analyzer/.env`

**Required Variables:**
- `OPENAI_API_BASE`
- `OPENAI_API_KEY`
- `MODEL_ID`
- `CONTEXT_STUDIO_ENABLED`
- `CONTEXT_STUDIO_MCP_URL`
- `CONTEXT_STUDIO_MCP_TOKEN`
- `CONTEXT_STUDIO_CONTEXT_ID`
- `CONTEXT_STUDIO_AGENT_PERSONA`
- `CONTEXT_STUDIO_API_KEY`
- `OBSERVABILITY_ENABLED`
- `OBSERVABILITY_PHOENIX_ENDPOINT`
- `OBSERVABILITY_PHOENIX_API_KEY`

**Additional Dependencies:**
- Observability tools (OpenTelemetry, Arize Phoenix)
- Context Studio integration

### Document Consolidator Module
**Location:** `document-consolidator/phase0_router/.env`

**Required Variables:**
- `OPENAI_API_BASE`
- `OPENAI_API_KEY`
- `MODEL_ID`

**Additional Dependencies:**
- `pypdf` - PDF text extraction
- `python-docx` - DOCX extraction
- `openpyxl` - XLSX extraction
- `python-multipart` - File uploads

## Best Practices

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use `.env.template`** - Always update the template when adding new variables
3. **Module isolation** - Each module should have its own `.env` file
4. **Shared dependencies** - Keep common dependencies in `requirements-base.txt`
5. **Documentation** - Document any new environment variables in this README

## Security Notes

- All `.env` files are excluded from git via `.gitignore`
- API keys and tokens should never be hardcoded
- Use environment variables for all sensitive configuration
- Rotate credentials regularly
- Use different credentials for development and production

## Getting Started

1. **Copy the template:**
   ```bash
   cp common/.env.template <your-module>/.env
   ```

2. **Fill in your credentials:**
   Edit the `.env` file with your actual API keys and configuration

3. **Install dependencies:**
   ```bash
   pip install -r common/requirements-base.txt
   pip install -r <your-module>/requirements.txt
   ```

4. **Verify configuration:**
   ```bash
   python <your-module>/run.py
   ```

## Support

For questions or issues with configuration:
1. Check the module-specific README files
2. Review the `.env.template` comments
3. Consult the project documentation

---
*Last updated: 2026-06-20*