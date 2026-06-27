# Knowledge Base MCP Server

A Model Context Protocol (MCP) server that provides semantic search and knowledge retrieval for organizational context in the RFP Analyzer.

## Features

- **Semantic Search**: Search across organizational knowledge base (standards, past RFPs, domain knowledge)
- **Compliance Standards**: Retrieve detailed compliance framework information
- **Similar RFP Matching**: Find past RFPs similar to current requirements
- **Document Indexing**: Add new documents to the knowledge base

## Installation

### Prerequisites

1. Python 3.10 or higher
2. MCP package installed (already available in your environment)

### Verify Installation

```bash
cd rfp-analyzer
python -c "from mcp.server import Server; print('MCP Server available')"
```

## Configuration

### MCP Server Configuration

The server can be configured in your MCP client (e.g., Claude Desktop) using the provided [`config.json`](config.json):

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["-m", "mcp_servers.knowledge_base_server"],
      "env": {
        "CONTEXT_ROOT": "./org_context",
        "PYTHONPATH": "."
      }
    }
  }
}
```

### Environment Variables

- `CONTEXT_ROOT`: Path to organizational context directory (default: `./org_context`)
- `PYTHONPATH`: Should include the rfp-analyzer root directory

## Testing

### Run Test Suite

Test the Knowledge Base server functionality without requiring full MCP setup:

```bash
cd rfp-analyzer
python mcp_servers/knowledge_base_server/test_kb_server.py
```

### Test Results

The test suite validates:
- ✅ Knowledge Base Statistics - Lists available documents
- ✅ Search Org Knowledge - Searches for keywords across all categories
- ⚠️ Get Compliance Standard - Retrieves compliance frameworks (requires HIPAA.md file)
- ⚠️ Find Similar RFPs - Finds similar past RFPs (requires past RFP files)
- ✅ Index Document - Adds new documents to knowledge base

**Note**: Some tests may fail if specific files (HIPAA standards, past RFPs) are not present in your knowledge base. This is expected behavior.

## Usage

### Standalone Mode (Testing)

Run the server directly for testing:

```bash
cd rfp-analyzer
python -m mcp_servers.knowledge_base_server
```

### MCP Client Mode

When configured in an MCP client (like Claude Desktop), the server provides these tools:

#### 1. search_org_knowledge

Search organizational knowledge base using keywords.

**Parameters**:
- `query` (string, required): Search query
- `category` (string, optional): Category to search ("all", "standards", "past_rfps", "domain_knowledge")
- `top_k` (integer, optional): Number of results to return (default: 5)

**Example**:
```json
{
  "query": "authentication",
  "category": "standards",
  "top_k": 3
}
```

#### 2. get_compliance_standard

Retrieve detailed compliance standard information.

**Parameters**:
- `framework` (string, required): Framework name (e.g., "GDPR", "HIPAA", "SOC2")

**Example**:
```json
{
  "framework": "HIPAA"
}
```

#### 3. find_similar_past_rfps

Find similar past RFPs based on description.

**Parameters**:
- `description` (string, required): RFP description to match against
- `top_k` (integer, optional): Number of similar RFPs to return (default: 3)

**Example**:
```json
{
  "description": "Healthcare patient portal with secure authentication",
  "top_k": 3
}
```

#### 4. index_document

Add a new document to the knowledge base.

**Parameters**:
- `file_path` (string, required): Path to document to index
- `category` (string, required): Category ("standards", "past_rfps", "domain_knowledge")
- `metadata` (object, optional): Additional metadata

**Example**:
```json
{
  "file_path": "./new_standard.md",
  "category": "standards",
  "metadata": {
    "type": "security",
    "version": "1.0"
  }
}
```

## Knowledge Base Structure

The server expects the following directory structure:

```
org_context/
├── standards/              # Organizational standards
│   ├── coding_standards.md
│   ├── security_standards.md
│   └── README.md
├── examples/               # Example documents
│   ├── past_rfps/         # Past RFP responses
│   └── README.md
├── domain_knowledge/       # Domain-specific knowledge
│   ├── healthcare_terminology.md
│   └── ...
└── config/                 # Configuration files
    └── org_config.yaml
```

## Current Test Results

Based on the latest test run:

```
[PASS]  Knowledge Base Stats     - 5 files indexed
[PASS]  Search Org Knowledge     - 3 results found for "authentication"
[FAIL]  Get Compliance Standard  - HIPAA standard not found (add HIPAA.md)
[FAIL]  Find Similar RFPs        - No past RFPs found (add to examples/past_rfps/)
[PASS]  Index Document           - Successfully indexed test document

Results: 3/5 tests passed
```

### To Improve Test Results

1. **Add HIPAA Compliance Standard**:
   ```bash
   # Create HIPAA standard file
   echo "# HIPAA Compliance Standard" > org_context/standards/HIPAA.md
   ```

2. **Add Past RFPs**:
   ```bash
   # Add sample past RFPs
   mkdir -p org_context/examples/past_rfps
   # Copy your past RFP files here
   ```

## Integration with RFP Analyzer

### Current Status

The Knowledge Base server is **implemented but not integrated** into the RFP analysis workflow.

### To Integrate

To use the Knowledge Base server during RFP analysis, you would need to:

1. **Add MCP Client** to the agents
2. **Call MCP Tools** during extraction
3. **Enhance Context** with retrieved knowledge

Example integration in `agents/compliance.py`:

```python
from mcp_client import call_mcp_tool

def extract_compliance(chunks, org_context):
    # Get compliance standards from Knowledge Base
    hipaa_info = call_mcp_tool(
        "knowledge-base",
        "get_compliance_standard",
        framework="HIPAA"
    )
    
    # Use retrieved info to enhance extraction
    # ... existing extraction logic
```

## Troubleshooting

### Issue: "MCP not available"

**Solution**: The MCP package is already installed in your environment. If you see this error, ensure you're running from the correct directory.

### Issue: "Context directory not found"

**Solution**: Ensure the `CONTEXT_ROOT` environment variable points to the correct path:
```bash
export CONTEXT_ROOT="./org_context"  # Linux/Mac
set CONTEXT_ROOT=./org_context       # Windows
```

### Issue: Unicode encoding errors on Windows

**Solution**: The test script automatically handles this. If you still see errors, run:
```bash
set PYTHONIOENCODING=utf-8
python mcp_servers/knowledge_base_server/test_kb_server.py
```

## Production Enhancements

For production use, consider adding:

1. **Vector Database Integration**
   - ChromaDB or Pinecone for semantic search
   - Better similarity matching

2. **Advanced Embedding Models**
   - sentence-transformers for better embeddings
   - Custom domain-specific models

3. **Caching Layer**
   - Redis for frequently accessed documents
   - Reduce latency

4. **Authentication**
   - API keys for secure access
   - Role-based access control

## Files

- [`server.py`](server.py) - Main MCP server implementation
- [`__main__.py`](__main__.py) - Entry point for running as module
- [`config.json`](config.json) - MCP server configuration
- [`test_kb_server.py`](test_kb_server.py) - Test suite
- [`README.md`](README.md) - This file

## Support

For issues or questions:
1. Check the test results: `python mcp_servers/knowledge_base_server/test_kb_server.py`
2. Review the logs in the test output
3. Ensure your knowledge base structure matches the expected format

---

**Status**: ✅ Implemented and Tested (3/5 tests passing)
**Integration**: ⚠️ Not yet integrated into RFP analysis workflow