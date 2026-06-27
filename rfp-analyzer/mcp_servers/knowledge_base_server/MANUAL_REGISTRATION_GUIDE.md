# Manual Server Registration in ContextForge

This guide explains how to manually register an MCP server in ContextForge using the web UI.

## Prerequisites

- ContextForge running at http://localhost:4444
- Admin access to ContextForge
- Your MCP server implementation ready

## Step-by-Step Registration Process

### 1. Access the Admin Interface

1. Open your browser and navigate to: **http://localhost:4444/admin**
2. Log in with your admin credentials (default: `admin@example.com`)

### 2. Navigate to Servers Section

1. Look for the **"Servers"** menu item in the left sidebar or top navigation
2. Click on **"Servers"** (NOT "MCP Registry" - that's for browsing available servers)
3. You should see a list of currently registered servers

### 3. Add a New Server

1. Click the **"Add Server"** or **"+ New Server"** button
2. Fill in the server details:

#### Basic Information

- **Name**: `knowledge-base` (unique identifier, lowercase with hyphens)
- **Display Name**: `Knowledge Base Server` (human-readable name)
- **Description**: `Knowledge Base MCP Server for RFP Analyzer organizational context`
- **Icon**: (optional) You can leave this blank or add an emoji/icon

#### Server Configuration

- **Command**: `python`
- **Arguments**: `-m mcp_servers.knowledge_base_server`
  - Or as array: `["-m", "mcp_servers.knowledge_base_server"]`
- **Working Directory**: `c:/Agents/CForgeEnv/rfp-analyzer`
  - This is the absolute path to your rfp-analyzer directory

#### Environment Variables

Add these environment variables (click "Add Environment Variable" for each):

1. **Key**: `CONTEXT_ROOT`  
   **Value**: `./org_context`

2. **Key**: `PYTHONPATH`  
   **Value**: `.`

#### Access Control

- **Team**: Select your team from the dropdown (e.g., "Default Team")
- **Owner Email**: `admin@example.com` (or your email)
- **Visibility**: `team` (visible to team members)

#### Status

- **Enabled**: ✓ Check this box to enable the server

### 4. Save the Server

1. Click **"Save"** or **"Create Server"** button
2. You should see a success message
3. The server should now appear in your servers list

### 5. Test the Server Connection

1. Find your newly registered server in the list
2. Click on it to view details
3. Look for a **"Test Connection"** or **"Start Server"** button
4. Click it to verify the server starts correctly
5. Check the logs for any errors

### 6. View Available Tools

Once the server is running:

1. Navigate to **"Tools"** section in the admin interface
2. You should see 4 tools from the knowledge-base server:
   - `search_org_knowledge`
   - `get_compliance_standard`
   - `find_similar_past_rfps`
   - `index_document`

## Alternative: Using the API

If you prefer to register via API, you can use curl:

```bash
curl -X POST http://localhost:4444/api/servers \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -d '{
    "name": "knowledge-base",
    "description": "Knowledge Base MCP Server for RFP Analyzer",
    "command": "python",
    "args": ["-m", "mcp_servers.knowledge_base_server"],
    "cwd": "c:/Agents/CForgeEnv/rfp-analyzer",
    "env": {
      "CONTEXT_ROOT": "./org_context",
      "PYTHONPATH": "."
    },
    "team_id": "YOUR_TEAM_ID",
    "owner_email": "admin@example.com",
    "visibility": "team",
    "enabled": true
  }'
```

## Alternative: Direct Database Registration

If the UI is not working, you can register directly in the database:

```python
import sqlite3
import json
from datetime import datetime
import uuid

# Connect to database
conn = sqlite3.connect('mcpgateway/mcp.db')
cursor = conn.cursor()

# Server details
server_id = str(uuid.uuid4())
now = datetime.utcnow().isoformat() + '+00:00'

# Insert server
cursor.execute("""
    INSERT INTO servers (
        id, name, description, icon, created_at, updated_at,
        enabled, tags, team_id, owner_email, visibility, version
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    server_id,
    'knowledge-base',
    'Knowledge Base MCP Server for RFP Analyzer organizational context',
    None,
    now,
    now,
    1,  # enabled
    '[]',  # empty tags array (important: must be valid JSON array)
    'YOUR_TEAM_ID',  # replace with your team ID
    'admin@example.com',
    'team',
    1
))

conn.commit()
conn.close()

print(f"Server registered with ID: {server_id}")
```

## Troubleshooting

### Server Not Visible in UI

**Problem**: Server registered but not showing in the UI

**Solutions**:
1. **Check tags format**: Tags must be an empty array `[]` or array of objects, not strings
   ```python
   # Fix tags in database
   cursor.execute("UPDATE servers SET tags='[]' WHERE name='knowledge-base'")
   ```

2. **Check team assignment**: Server must have a valid `team_id`
   ```python
   # Update team assignment
   cursor.execute("""
       UPDATE servers 
       SET team_id='YOUR_TEAM_ID', 
           owner_email='admin@example.com',
           visibility='team'
       WHERE name='knowledge-base'
   """)
   ```

3. **Refresh browser**: Hard refresh (Ctrl+Shift+R) or clear cache

### Validation Errors

**Problem**: "Input should be a valid dictionary" error for tags

**Solution**: The tags field expects an array of objects, not strings. Clear tags:
```sql
UPDATE servers SET tags='[]' WHERE name='knowledge-base';
```

### Server Won't Start

**Problem**: Server registered but fails to start

**Check**:
1. **Working directory**: Must be absolute path to rfp-analyzer
2. **Python path**: Ensure Python is in system PATH
3. **Dependencies**: Run `pip install -r requirements.txt` in rfp-analyzer
4. **Environment variables**: Verify CONTEXT_ROOT and PYTHONPATH are set

### Tools Not Appearing

**Problem**: Server starts but tools don't show up

**Check**:
1. Server logs for errors
2. MCP protocol initialization
3. Tool registration in server code
4. Refresh the Tools page in admin UI

## Getting Your Team ID

To find your team ID:

```python
import sqlite3

conn = sqlite3.connect('mcpgateway/mcp.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name FROM teams")
teams = cursor.fetchall()

for team_id, team_name in teams:
    print(f"Team: {team_name}, ID: {team_id}")

conn.close()
```

Or via SQL:
```sql
SELECT id, name FROM teams;
```

## Verifying Registration

After registration, verify with:

```python
import sqlite3

conn = sqlite3.connect('mcpgateway/mcp.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, name, enabled, team_id, owner_email, visibility, tags
    FROM servers 
    WHERE name='knowledge-base'
""")

result = cursor.fetchone()
if result:
    print("Server found:")
    print(f"  ID: {result[0]}")
    print(f"  Name: {result[1]}")
    print(f"  Enabled: {result[2]}")
    print(f"  Team ID: {result[3]}")
    print(f"  Owner: {result[4]}")
    print(f"  Visibility: {result[5]}")
    print(f"  Tags: {result[6]}")
else:
    print("Server not found")

conn.close()
```

## Next Steps

After successful registration:

1. **Test the server** - Use the Test Connection button
2. **Try the tools** - Navigate to Tools section and test each tool
3. **Configure clients** - Add server to Claude Desktop or other MCP clients
4. **Monitor logs** - Check server logs for any issues
5. **Use in workflows** - Integrate tools into your RFP analysis workflow

## Support

If you encounter issues:

1. Check ContextForge logs in the terminal
2. Check server logs (if available)
3. Verify database entries with the verification script above
4. Ensure all prerequisites are met
5. Try restarting ContextForge

## Summary

The key steps are:
1. ✅ Access admin UI at http://localhost:4444/admin
2. ✅ Navigate to "Servers" section
3. ✅ Click "Add Server"
4. ✅ Fill in all required fields (name, command, args, working directory)
5. ✅ Set environment variables (CONTEXT_ROOT, PYTHONPATH)
6. ✅ Assign to team and set visibility
7. ✅ Enable the server
8. ✅ Save and test connection
9. ✅ Verify tools appear in Tools section

Your server should now be registered and ready to use! 🎉