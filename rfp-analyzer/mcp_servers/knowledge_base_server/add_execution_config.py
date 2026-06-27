"""
Add execution configuration to the knowledge-base server in ContextForge database.
This will allow the server to be started from the UI.
"""

import sqlite3
import json
import sys
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "mcpgateway" / "mcp.db"

# Server configuration
SERVER_NAME = "knowledge-base"
COMMAND = "python"
ARGS = ["-m", "mcp_servers.knowledge_base_server"]
WORKING_DIR = str(Path(__file__).parent.parent.parent.resolve())
ENV_VARS = {
    "CONTEXT_ROOT": "./org_context",
    "PYTHONPATH": "."
}

def add_execution_config():
    """Add execution configuration to the server."""
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at: {DB_PATH}")
        print("Make sure ContextForge is installed in the correct location.")
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if server exists
        cursor.execute("SELECT id, name FROM servers WHERE name=?", (SERVER_NAME,))
        server = cursor.fetchone()
        
        if not server:
            print(f"❌ Server '{SERVER_NAME}' not found in database")
            print("Please register the server first using register_in_contextforge.py")
            return False
        
        server_id, server_name = server
        print(f"✓ Found server: {server_name} (ID: {server_id})")
        
        # Check if execution_configs table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='execution_configs'
        """)
        
        if not cursor.fetchone():
            print("❌ execution_configs table not found")
            print("This version of ContextForge may not support execution configs in database")
            print("\nYou need to configure the server manually in the UI:")
            print(f"  Command: {COMMAND}")
            print(f"  Args: {' '.join(ARGS)}")
            print(f"  Working Directory: {WORKING_DIR}")
            print(f"  Environment Variables:")
            for key, value in ENV_VARS.items():
                print(f"    {key}={value}")
            return False
        
        # Insert or update execution config
        cursor.execute("""
            INSERT OR REPLACE INTO execution_configs 
            (server_id, command, args, cwd, env, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            server_id,
            COMMAND,
            json.dumps(ARGS),
            WORKING_DIR,
            json.dumps(ENV_VARS)
        ))
        
        conn.commit()
        
        print("\n✅ Execution configuration added successfully!")
        print(f"\nConfiguration:")
        print(f"  Command: {COMMAND}")
        print(f"  Args: {' '.join(ARGS)}")
        print(f"  Working Directory: {WORKING_DIR}")
        print(f"  Environment Variables:")
        for key, value in ENV_VARS.items():
            print(f"    {key}={value}")
        
        print("\n📝 Next steps:")
        print("1. Refresh your browser at http://localhost:4444/admin")
        print("2. Go to the server details page")
        print("3. Click 'Start Server' button")
        print("4. Wait for status to change to 'Active'")
        print("5. Check Tools section for the 4 available tools")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Adding Execution Configuration to Knowledge Base Server")
    print("=" * 70)
    print()
    
    success = add_execution_config()
    
    if not success:
        print("\n⚠️  Configuration could not be added to database")
        print("You'll need to configure the server manually in the UI")
        print("\nManual Configuration:")
        print(f"  Command: {COMMAND}")
        print(f"  Args: {' '.join(ARGS)}")
        print(f"  Working Directory: {WORKING_DIR}")
        print(f"  Environment Variables:")
        for key, value in ENV_VARS.items():
            print(f"    {key}={value}")
        sys.exit(1)
    
    sys.exit(0)

# Made with Bob
