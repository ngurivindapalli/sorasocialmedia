#!/usr/bin/env python3
"""
Start Hyperspell MCP Server
Run this script to start the MCP server for AI clients like Claude Desktop, Cursor, etc.

Usage:
    python start_mcp_server.py

Or configure in Claude Desktop config.json:
{
  "mcpServers": {
    "hyperspell": {
      "command": "python",
      "args": ["/path/to/backend/services/hyperspell_mcp_server.py"],
      "env": {
        "HYPERSPELL_API_KEY": "Your_API_Key",
        "HYPERSPELL_USER_ID": "Your_User_ID"
      }
    }
  }
}
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.hyperspell_mcp_server import main

if __name__ == "__main__":
    main()



