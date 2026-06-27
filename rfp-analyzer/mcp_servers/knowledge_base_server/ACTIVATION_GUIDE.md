# How to Activate the Knowledge Base Server in ContextForge

The server is registered but shows as "inactive" because it needs execution configuration.

## Quick Activation Steps

### 1. You're Already on the Server Details Page! ✅

You should see the server details for "knowledge-base" at:
`http://localhost:4444/admin/servers/8ded25e1-7c62-43e4-95e7-3c0166c6bea1`

### 2. Look for "Edit" or "Configure" Button

On the server details page, look for:
- **"Edit Server"** button (usually top-right)
- **"Configure"** button
- **"Settings"** tab or section

Click it to enter edit mode.

### 3. Fill in Execution Configuration

You need to add these fields:

#### Command Configuration
```
Command: python
```

#### Arguments (choose ONE format)

**Option A - Single string:**
```
Arguments: -m mcp_servers.knowledge_base_server
```

**Option B - JSON array (if UI requires):**
```json
["-m", "mcp_servers.knowledge_base_server"]
```

#### Working Directory
```
Working Directory: c:/Agents/CForgeEnv/rfp-analyzer
```
⚠️ **Important**: Use the FULL absolute path, not relative path!

#### Environment Variables

Click "Add Environment Variable" for each:

1. **Variable 1:**
   - Name: `CONTEXT_ROOT`
   - Value: `./org_context`

2. **Variable 2:**
   - Name: `PYTHONPATH`
   - Value: `.`

### 4. Save Configuration

Click **"Save"** or **"Update Server"** button at the bottom.

### 5. Start the Server

After saving, you should see:
- **"Start Server"** button
- **"Test Connection"** button
- Or the server may auto-start

Click **"Start Server"** to activate it.

### 6. Verify Activation

Once started, you should see:
- Status changes from "Inactive" to **"Active"** or **"Running"**
- Green indicator or checkmark
- Server logs appear (if available)
- Tools become available in the Tools section

## Alternative: Use the Edit Form Directly

If you see an edit form on the current page, fill in these fields directly:

### Basic Information (already filled)
- ✅ Name: `knowledge-base`
- ✅ Description: Already set
- ✅ Team: Already assigned
- ✅ Enabled: Already checked

### Execution Configuration (NEEDS TO BE FILLED)
- **Command**: `python`
- **Arguments**: `-m mcp_servers.knowledge_base_server`
- **Working Directory**: `c:/Agents/CForgeEnv/rfp-analyzer`

### Environment Variables (NEEDS TO BE ADDED)
Click "Add Environment Variable" twice:
1. `CONTEXT_ROOT` = `./org_context`
2. `PYTHONPATH` = `.`

### Save and Start
1. Click **"Save"** at the bottom
2. Click **"Start Server"** button that appears
3. Wait for status to change to "Active"

## Troubleshooting

### Server Won't Start

**Check these:**

1. **Python Path**: Ensure `python` command works in your terminal
   ```bash
   python --version
   ```

2. **Working Directory**: Must be absolute path to rfp-analyzer
   ```
   c:/Agents/CForgeEnv/rfp-analyzer
   ```

3. **Dependencies**: Ensure packages are installed
   ```bash
   cd c:/Agents/CForgeEnv/rfp-analyzer
   pip install -r requirements.txt
   ```

4. **Context Directory**: Verify org_context exists
   ```bash
   dir c:/Agents/CForgeEnv/rfp-analyzer/org_context
   ```

### Server Starts But No Tools

**Check:**
1. Server logs for errors
2. MCP protocol initialization
3. Refresh the Tools page

### Can't Find Edit Button

**Try:**
1. Look for **"⚙️ Settings"** icon
2. Look for **"✏️ Edit"** icon
3. Look for **"Configure"** link
4. Check if there's a dropdown menu (⋮) with "Edit" option

## What You Should See After Activation

### Server Status
- ✅ Status: **Active** or **Running**
- ✅ Green indicator
- ✅ Last started timestamp

### Available Tools (in Tools section)
1. `search_org_knowledge` - Search organizational knowledge base
2. `get_compliance_standard` - Get compliance standards
3. `find_similar_past_rfps` - Find similar past RFPs
4. `index_document` - Index new documents

### Server Logs
You should see logs showing:
```
MCP server started
Initialized knowledge base
Ready to accept connections
```

## Quick Test After Activation

Once active, test a tool:

1. Go to **Tools** section in admin UI
2. Find `search_org_knowledge` tool
3. Click **"Test"** or **"Try It"**
4. Enter test query: `healthcare`
5. Click **"Execute"**
6. You should see search results

## Summary

**Current Status**: Server is registered and enabled ✅  
**What's Missing**: Execution configuration (command, args, working directory) ❌  
**Action Needed**: Fill in execution config and click "Start Server" 🚀

The server is ready to go - it just needs you to tell ContextForge HOW to run it!