# RFP Analyzer MCP Server Setup Guide

This guide explains how to expose your RFP Analyzer application as an MCP server and integrate it with IBM ICA MCP Gateway.

## Overview

The MCP server wraps your RFP Analyzer functionality and exposes it as JSON-RPC tools that can be called by AI agents through the IBM ICA MCP Gateway.

### Available MCP Tools

1. **`analyze_rfp`** - Start an RFP analysis job
2. **`get_analysis_status`** - Check the status of an analysis
3. **`get_analysis_results`** - Retrieve completed analysis results
4. **`list_analyses`** - List all analyses

## Prerequisites

1. Python 3.8+ installed
2. RFP Analyzer dependencies installed (see main README.md)
3. IBM ICA MCP Gateway account and credentials
4. OpenAI API key (for the RFP Analyzer)

## Step 1: Install MCP Server Dependencies

```bash
cd rfp-analyzer
pip install -r mcp_requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pydantic (data validation)
- python-dotenv (environment variables)

## Step 2: Configure Environment Variables

Make sure your `.env` file includes:

```bash
# Required for RFP Analyzer
OPENAI_API_KEY=your-openai-api-key

# Optional: Custom port for MCP server
MCP_SERVER_PORT=8001
```

## Step 3: Start the MCP Server Locally

### On Windows:
```bash
start_mcp_server.bat
```

### On Linux/Mac:
```bash
chmod +x start_mcp_server.sh
./start_mcp_server.sh
```

### Or directly with Python:
```bash
python mcp_server.py
```

The server will start on `http://localhost:8001` by default.

### Verify Server is Running

Open your browser and visit:
- Health check: http://localhost:8001/health
- API docs: http://localhost:8001/docs
- Root info: http://localhost:8001/

## Step 4: Test the MCP Server Locally

Run the test suite to verify all tools work correctly:

```bash
# Basic tests (without file analysis)
python test_mcp_server.py

# Full tests with a sample RFP file
python test_mcp_server.py path/to/sample_rfp.pdf
```

Expected output:
```
==========================================
RFP Analyzer MCP Server - Test Suite
==========================================

TEST 1: Health Check
✓ Server is healthy

TEST 2: List Available Tools
✓ Found 4 tools:
  - analyze_rfp
  - get_analysis_status
  - get_analysis_results
  - list_analyses

TEST SUMMARY
✓ PASS Health Check
✓ PASS Tools List
...
```

## Step 5: Expose Server to IBM ICA MCP Gateway

### Option A: Using ngrok (for testing)

1. Install ngrok: https://ngrok.com/download

2. Start ngrok tunnel:
```bash
ngrok http 8001
```

3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

4. Your MCP endpoint will be: `https://abc123.ngrok.io/mcp`

### Option B: Deploy to Cloud (production)

Deploy the MCP server to a cloud platform:

**AWS EC2/ECS:**
```bash
# Build Docker image
docker build -t rfp-analyzer-mcp .

# Run container
docker run -p 8001:8001 \
  -e OPENAI_API_KEY=your-key \
  rfp-analyzer-mcp
```

**Azure App Service:**
```bash
az webapp up --name rfp-analyzer-mcp \
  --runtime "PYTHON:3.11" \
  --sku B1
```

**Google Cloud Run:**
```bash
gcloud run deploy rfp-analyzer-mcp \
  --source . \
  --platform managed \
  --region us-central1
```

## Step 6: Register with IBM ICA MCP Gateway

### Using IBM ICA Web Console

1. Log in to IBM ICA MCP Gateway console
2. Navigate to "MCP Servers" section
3. Click "Add New Server"
4. Fill in the details:
   - **Name**: RFP Analyzer
   - **Description**: AI-powered RFP analysis and requirement extraction
   - **MCP Endpoint URL**: `https://your-server.com/mcp`
   - **Authentication**: Bearer token (if configured)
5. Click "Test Connection" to verify
6. Save the server configuration

### Using IBM ICA CLI

```bash
# Install IBM ICA CLI
npm install -g @ibm/ica-cli

# Login
ica login

# Register MCP server
ica mcp register \
  --name "RFP Analyzer" \
  --endpoint "https://your-server.com/mcp" \
  --description "AI-powered RFP analysis"

# List registered servers
ica mcp list

# Test the server
ica mcp test <server-id>
```

## Step 7: Use from Your Agent

Update your agent code to connect to the RFP Analyzer MCP server:

```python
from src.agents.base_with_mcp import BaseAgentWithMCP

# Create agent with MCP connection
agent = BaseAgentWithMCP(
    name="rfp_assistant",
    system_prompt="You are an RFP analysis assistant...",
    mcp_server_url="https://ica-gateway.ibm.com/servers/<server-id>/mcp",
    mcp_authorization="Bearer <your-token>"
)

# The agent will automatically discover and use RFP Analyzer tools
response = agent.process_request(
    "Analyze the RFP document at /path/to/rfp.pdf"
)
```

## MCP Tool Usage Examples

### 1. Analyze an RFP

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "analyze_rfp",
    "arguments": {
      "file_path": "/path/to/rfp.pdf",
      "title": "Project Alpha RFP",
      "output_format": "both",
      "min_confidence": 0.5
    }
  },
  "id": 1
}
```

Response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"success\": true, \"job_id\": \"abc-123\", \"status\": \"pending\"}"
    }]
  },
  "id": 1
}
```

### 2. Check Analysis Status

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_analysis_status",
    "arguments": {
      "job_id": "abc-123"
    }
  },
  "id": 2
}
```

### 3. Get Results

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_analysis_results",
    "arguments": {
      "job_id": "abc-123",
      "format": "summary"
    }
  },
  "id": 3
}
```

### 4. List All Analyses

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "list_analyses",
    "arguments": {
      "limit": 10,
      "status": "completed"
    }
  },
  "id": 4
}
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent (LangGraph)                      │
│                  (Your main application)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ JSON-RPC over HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              IBM ICA MCP Gateway                             │
│              (Manages MCP servers)                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ JSON-RPC
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           RFP Analyzer MCP Server (FastAPI)                  │
│           - Exposes 4 MCP tools                              │
│           - Runs on localhost:8001 or cloud                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ Python function calls
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           RFP Analyzer Core (LangGraph)                      │
│           - Multi-agent analysis system                      │
│           - Document parsing & extraction                    │
│           - Requirement categorization                       │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Server won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Install dependencies: `pip install -r mcp_requirements.txt`

**Error**: `Address already in use`
- **Solution**: Change port: `export MCP_SERVER_PORT=8002` (or edit `.env`)

### Tools not discovered

**Error**: Agent can't find RFP Analyzer tools
- **Solution**: Verify MCP endpoint URL is correct
- **Solution**: Check server is running: `curl http://localhost:8001/health`
- **Solution**: Test tools/list: `curl -X POST http://localhost:8001/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'`

### Analysis fails

**Error**: `OPENAI_API_KEY not set`
- **Solution**: Add API key to `.env` file

**Error**: `File not found`
- **Solution**: Use absolute paths or ensure file is accessible to server

### IBM ICA Gateway connection fails

**Error**: `Connection refused` or `404 Not Found`
- **Solution**: Verify your server is publicly accessible (use ngrok for testing)
- **Solution**: Check firewall rules allow inbound traffic on port 8001
- **Solution**: Ensure HTTPS is configured (IBM ICA may require HTTPS)

## Security Considerations

1. **Authentication**: Add bearer token authentication to protect your MCP server
2. **HTTPS**: Always use HTTPS in production (required by IBM ICA)
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Input Validation**: The server validates all inputs, but review for your use case
5. **File Access**: Restrict file system access to specific directories

## Next Steps

1. ✅ Start MCP server locally
2. ✅ Test with `test_mcp_server.py`
3. ✅ Expose server (ngrok or cloud deployment)
4. ✅ Register with IBM ICA MCP Gateway
5. ✅ Update your agent to use the MCP server
6. ✅ Test end-to-end workflow

## Support

For issues or questions:
- Check server logs: `./logs/rfp_analyzer.log`
- Review FastAPI docs: http://localhost:8001/docs
- Test with curl or Postman
- Check IBM ICA MCP Gateway documentation

---

**Congratulations!** Your RFP Analyzer is now available as an MCP server that can be called by any AI agent through IBM ICA MCP Gateway! 🎉