"""
Register Knowledge Base MCP Server in ContextForge
---------------------------------------------------
This script registers the Knowledge Base server in your ContextForge gateway.
"""

import sqlite3
import uuid
from datetime import datetime, timezone
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')  # type: ignore
        sys.stderr.reconfigure(encoding='utf-8')  # type: ignore

# Path to ContextForge database
DB_PATH = Path(__file__).parent.parent.parent.parent / "mcpgateway" / "mcp.db"

def register_server():
    """Register the Knowledge Base server in ContextForge."""
    
    if not DB_PATH.exists():
        print(f"Error: ContextForge database not found at {DB_PATH}")
        print("Make sure ContextForge is installed and initialized.")
        return False
    
    print(f"Connecting to ContextForge database: {DB_PATH}")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Check if server already exists
        cursor.execute("SELECT id, name FROM servers WHERE name = ?", ("knowledge-base",))
        existing = cursor.fetchone()
        
        if existing:
            print(f"\n[WARN] Server 'knowledge-base' already registered with ID: {existing[0]}")
            print("Do you want to update it? (y/n): ", end="")
            response = input().strip().lower()
            
            if response != 'y':
                print("Registration cancelled.")
                conn.close()
                return False
            
            # Update existing server
            now = datetime.now(timezone.utc).isoformat()
            cursor.execute('''
                UPDATE servers 
                SET description = ?,
                    updated_at = ?,
                    enabled = ?,
                    tags = ?
                WHERE id = ?
            ''', (
                'Knowledge Base MCP Server for RFP Analyzer organizational context',
                now,
                True,
                '["rfp-analyzer", "knowledge-base", "organizational-context"]',
                existing[0]
            ))
            
            conn.commit()
            print(f"\n[OK] Server updated successfully!")
            print(f"   ID: {existing[0]}")
            print(f"   Name: knowledge-base")
            
        else:
            # Insert new server
            server_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute('''
                INSERT INTO servers (
                    id, name, description, created_at, updated_at,
                    enabled, tags, version, visibility
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                server_id,
                'knowledge-base',
                'Knowledge Base MCP Server for RFP Analyzer organizational context',
                now,
                now,
                True,
                '["rfp-analyzer", "knowledge-base", "organizational-context"]',
                1,
                'private'  # Add visibility field
            ))
            
            conn.commit()
            print(f"\n[OK] Server registered successfully!")
            print(f"   ID: {server_id}")
            print(f"   Name: knowledge-base")
        
        # Show all registered servers
        cursor.execute("SELECT id, name, enabled FROM servers")
        servers = cursor.fetchall()
        
        print(f"\n[INFO] All Registered Servers ({len(servers)}):")
        print("-" * 60)
        for srv in servers:
            status = "[Enabled]" if srv[2] else "[Disabled]"
            print(f"   {srv[1]:<30} {status}")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Access your ContextForge web interface")
        print("2. Navigate to the Servers section")
        print("3. Configure the server execution details:")
        print("   - Command: python")
        print("   - Args: -m mcp_servers.knowledge_base_server")
        print("   - Working Dir: c:/Agents/CForgeEnv/rfp-analyzer")
        print("   - Env: CONTEXT_ROOT=./org_context, PYTHONPATH=.")
        print("4. Test the server connection")
        print("5. Use the server tools in your MCP clients")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error registering server: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  Knowledge Base MCP Server - ContextForge Registration")
    print("=" * 60)
    print()
    
    success = register_server()
    sys.exit(0 if success else 1)

# Made with Bob
