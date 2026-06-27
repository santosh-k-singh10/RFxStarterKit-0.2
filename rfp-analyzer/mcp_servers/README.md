# MCP Servers for RFP Analyzer

This directory contains MCP (Model Context Protocol) servers that extend the RFP Analyzer with advanced capabilities.

## Available Servers

### 1. Knowledge Base Server ✅ IMPLEMENTED
**Status**: Functional (simplified implementation)  
**Location**: `knowledge_base_server/`

**Capabilities**:
- Search organizational knowledge using keywords
- Retrieve compliance standards
- Find similar past RFPs
- Index new documents

**Usage**:
```python
from mcp_servers.knowledge_base_server.server import KnowledgeBaseServer

kb = KnowledgeBaseServer("./org_context")
results = kb.search_org_knowledge("authentication", category="standards")
```

### 2. Template Engine Server 🚧 TEMPLATE
**Status**: Template/skeleton provided  
**Location**: `template_engine_server/`

**Planned Capabilities**:
- Render requirements using Jinja2 templates
- Apply organizational branding
- Generate custom report sections
- Format outputs consistently

**To Implement**:
1. Install Jinja2: `pip install jinja2`
2. Create template files in `org_context/templates/`
3. Implement rendering logic in `server.py`
4. Add MCP tool definitions

### 3. Document Intelligence Server 🚧 TEMPLATE
**Status**: Template/skeleton provided  
**Location**: `doc_intelligence_server/`

**Planned Capabilities**:
- Extract tables from PDFs
- Analyze diagrams and images
- Extract metadata (deadlines, contacts)
- Parse document structure

**To Implement**:
1. Install dependencies: `pip install pdfplumber pytesseract pillow`
2. Implement table extraction logic
3. Add image analysis capabilities
4. Create MCP tool definitions

### 4. Cost Estimator Server 🚧 TEMPLATE
**Status**: Template/skeleton provided  
**Location**: `cost_estimator_server/`

**Planned Capabilities**:
- Estimate development effort using ML
- Calculate project costs
- Suggest team composition
- Reference historical data

**To Implement**:
1. Install dependencies: `pip install scikit-learn pandas`
2. Create historical data database
3. Train effort estimation model
4. Implement cost calculation logic
5. Add MCP tool definitions

## Architecture

```
RFP Analyzer
     │
     ├─> Knowledge Base Server (semantic search, standards)
     ├─> Template Engine Server (formatting, branding)
     ├─> Document Intelligence Server (tables, diagrams)
     └─> Cost Estimator Server (effort, cost, team)
```

## Installation

### Basic Setup (Knowledge Base only)
```bash
cd rfp-analyzer
pip install -r requirements.txt
```

### Full Setup (All servers)
```bash
# Install all dependencies
pip install -r requirements_mcp_full.txt

# Or install individually
pip install mcp jinja2 pdfplumber pytesseract pillow scikit-learn pandas chromadb sentence-transformers
```

## Configuration

### MCP Gateway Configuration

Add to your MCP gateway config (e.g., `mcpgateway/config.json`):

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "python",
      "args": ["-m", "rfp-analyzer.mcp_servers.knowledge_base_server.server"],
      "env": {
        "CONTEXT_ROOT": "./rfp-analyzer/org_context"
      }
    },
    "template-engine": {
      "command": "python",
      "args": ["-m", "rfp-analyzer.mcp_servers.template_engine_server.server"],
      "env": {
        "TEMPLATES_PATH": "./rfp-analyzer/org_context/templates"
      }
    },
    "doc-intelligence": {
      "command": "python",
      "args": ["-m", "rfp-analyzer.mcp_servers.doc_intelligence_server.server"]
    },
    "cost-estimator": {
      "command": "python",
      "args": ["-m", "rfp-analyzer.mcp_servers.cost_estimator_server.server"],
      "env": {
        "HISTORICAL_DATA": "./rfp-analyzer/org_context/historical_data.db"
      }
    }
  }
}
```

## Testing

### Test Knowledge Base Server
```bash
cd rfp-analyzer
python -m mcp_servers.knowledge_base_server.server
```

### Test Individual Functions
```python
from mcp_servers.knowledge_base_server.server import KnowledgeBaseServer

kb = KnowledgeBaseServer()

# Test search
results = kb.search_org_knowledge("authentication")
print(f"Found {len(results)} results")

# Test compliance retrieval
gdpr = kb.get_compliance_standard("GDPR")
print(f"GDPR standard: {gdpr}")

# Test similar RFPs
similar = kb.find_similar_past_rfps("healthcare portal with patient data")
print(f"Found {len(similar)} similar RFPs")
```

## Development Guide

### Adding a New MCP Tool

1. **Define the tool function** in your server class:
```python
def my_new_tool(self, param1: str, param2: int) -> dict:
    """Tool description."""
    # Implementation
    return {"result": "success"}
```

2. **Add MCP tool definition** (if using MCP):
```python
Tool(
    name="my_new_tool",
    description="What this tool does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string"},
            "param2": {"type": "integer"}
        },
        "required": ["param1"]
    }
)
```

3. **Add tool handler**:
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "my_new_tool":
        result = server_instance.my_new_tool(**arguments)
        return [TextContent(type="text", text=json.dumps(result))]
```

### Extending Knowledge Base with Vector Search

For production-grade semantic search:

```python
# Install ChromaDB
pip install chromadb sentence-transformers

# In server.py
import chromadb
from sentence_transformers import SentenceTransformer

class KnowledgeBaseServer:
    def __init__(self, context_root: str):
        # Initialize vector database
        self.chroma_client = chromadb.PersistentClient(
            path=f"{context_root}/vector_db"
        )
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.chroma_client.get_or_create_collection("knowledge")
    
    def search_org_knowledge(self, query: str, top_k: int = 5):
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Semantic search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results
```

## Troubleshooting

### MCP Not Available
If you see "MCP not available" warnings:
```bash
pip install mcp
```

### Import Errors
Ensure you're running from the correct directory:
```bash
cd rfp-analyzer
python -m mcp_servers.knowledge_base_server.server
```

### No Results from Search
1. Check that org_context directory exists
2. Add some markdown files to org_context/standards/
3. Verify file permissions

## Next Steps

1. **Complete Template Engine Server**
   - Implement Jinja2 template rendering
   - Add branding application logic
   - Create sample templates

2. **Complete Document Intelligence Server**
   - Implement PDF table extraction
   - Add image analysis
   - Create metadata extraction

3. **Complete Cost Estimator Server**
   - Build historical data database
   - Train ML model for effort estimation
   - Implement cost calculation

4. **Integration**
   - Update agents to call MCP tools
   - Add MCP client to main.py
   - Test end-to-end workflow

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Phase 2 Detailed Plan](../PHASE2_DETAILED_PLAN.md)
- [Integration Guide](../INTEGRATION_GUIDE.md)

## Support

For issues or questions:
1. Check server logs
2. Review Phase 2 implementation plan
3. Test individual functions before MCP integration