# Integrating Knowledge Base MCP Server with ContextForge

## Overview

ContextForge is your MCP Gateway that manages and routes MCP server connections. To view and use the Knowledge Base MCP server in ContextForge, you need to register it in the gateway.

## Current Status

Based on the check, **no MCP servers are currently registered** in your ContextForge instance.

## How to Register the Knowledge Base Server

### Option 1: Using ContextForge Web UI

1. **Access ContextForge**:
   - Your ContextForge gateway is running at the endpoint configured in `mcpgateway/.env`
   - Open the ContextForge web interface (typically at `http://localhost:PORT`)

2. **Register New Server**:
   - Navigate to "Servers" or "MCP Servers" section
   - Click "Add Server" or "Register Server"
   - Fill in the details:
     - **Name**: `knowledge-base`
     - **Description**: `Knowledge Base MCP Server for RFP Analyzer organizational context`
     - **Command**: `python`
     - **Args**: `-m mcp_servers.knowledge_base_server`
     - **Working Directory**: `c:/Agents/CForgeEnv/rfp-analyzer`
     - **Environment Variables**:
       - `CONTEXT_ROOT`: `./org_context`
       - `PYTHONPATH`: `.`

3. **Enable the Server**:
   - Toggle the "Enabled" switch
   - Save the configuration

### Option 2: Using ContextForge API

If ContextForge provides an API, you can register the server programmatically:

```python
import requests

# ContextForge API endpoint (adjust based on your setup)
api_url = "http://localhost:PORT/api/servers"

server_config = {
    "name": "knowledge-base",
    "description": "Knowledge Base MCP Server for RFP Analyzer",
    "enabled": True,
    "tags": ["rfp-analyzer", "knowledge-base", "organizational-context"],
    "config": {
        "command": "python",
        "args": ["-m", "mcp_servers.knowledge_base_server"],
        "cwd": "c:/Agents/CForgeEnv/rfp-analyzer",
        "env": {
            "CONTEXT_ROOT": "./org_context",
            "PYTHONPATH": "."
        }
    }
}

response = requests.post(api_url, json=server_config)
print(response.json())
```

### Option 3: Direct Database Registration

If you have direct database access, you can insert the server record:

```python
import sqlite3
import uuid
from datetime import datetime

conn = sqlite3.connect('mcpgateway/mcp.db')
cursor = conn.cursor()

server_id = str(uuid.uuid4())
now = datetime.utcnow().isoformat()

cursor.execute('''
    INSERT INTO servers (
        id, name, description, created_at, updated_at, 
        enabled, tags, version
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    server_id,
    'knowledge-base',
    'Knowledge Base MCP Server for RFP Analyzer organizational context',
    now,
    now,
    True,
    '["rfp-analyzer", "knowledge-base"]',
    1
))

conn.commit()
conn.close()

print(f"Server registered with ID: {server_id}")
```

## Verifying Registration

After registration, verify the server appears in ContextForge:

```bash
cd mcpgateway
python check_servers.py
```

You should see output like:
```
Registered Servers:
--------------------------------------------------------------------------------
id: <uuid>
name: knowledge-base
description: Knowledge Base MCP Server for RFP Analyzer organizational context
enabled: 1
...
```

## Using the Server in ContextForge

Once registered, you can:

1. **View Server Status**:
   - Check if the server is running
   - View connection logs
   - Monitor performance metrics

2. **Test Server Tools**:
   - Use ContextForge's tool testing interface
   - Call `search_org_knowledge`, `get_compliance_standard`, etc.
   - View responses and debug issues

3. **Connect from Clients**:
   - Configure Claude Desktop or other MCP clients to connect through ContextForge
   - Use the gateway URL instead of direct server connection

## ContextForge Configuration

Your ContextForge gateway configuration is in `mcpgateway/.env`. Key settings:

- **Database**: `mcp.db` (SQLite)
- **Port**: Check `.env` for the configured port
- **Authentication**: Check if authentication is enabled

## Troubleshooting

### Server Not Appearing

1. **Check ContextForge is Running**:
   ```bash
   # Your terminal shows it's running:
   cd mcpgateway && set PYTHONIOENCODING=utf-8 && .venv\Scripts\activate.bat && mcpgateway mcpgateway.main:app --env-file .env
   ```

2. **Verify Database Connection**:
   ```bash
   cd mcpgateway
   python check_servers.py
   ```

3. **Check Logs**:
   - Look for ContextForge logs
   - Check for registration errors

### Server Registration Fails

1. **Verify Python Path**:
   - Ensure Python can find the `mcp_servers` module
   - Check `PYTHONPATH` is set correctly

2. **Test Server Standalone**:
   ```bash
   cd rfp-analyzer
   python -m mcp_servers.knowledge_base_server
   ```

3. **Check Permissions**:
   - Ensure ContextForge has permission to execute Python
   - Verify file system permissions

## Next Steps

1. **Register the Server** using one of the methods above
2. **Test the Connection** through ContextForge
3. **Configure Clients** to use the server via ContextForge gateway
4. **Monitor Usage** through ContextForge's observability features

## Benefits of Using ContextForge

- **Centralized Management**: Manage all MCP servers in one place
- **Monitoring**: Track usage, performance, and errors
- **Security**: Centralized authentication and authorization
- **Routing**: Route requests to appropriate servers
- **Logging**: Comprehensive audit trails

## Additional Resources

- ContextForge Documentation: Check your ContextForge installation docs
- MCP Protocol Spec: https://modelcontextprotocol.io
- Knowledge Base Server README: [`README.md`](README.md)

---

**Status**: Ready to register in ContextForge
**Database**: `mcpgateway/mcp.db`
**Current Servers**: 0 registered