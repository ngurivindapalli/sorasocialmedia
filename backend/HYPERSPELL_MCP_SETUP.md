# Hyperspell MCP Server Setup

This guide explains how to set up and use the Hyperspell MCP (Model Context Protocol) server to connect your AI clients (like Claude Desktop, Cursor, etc.) to your Hyperspell memory layer.

## What is MCP?

The Model Context Protocol (MCP) is an open standard developed by Anthropic that allows AI applications to connect with external data sources and tools. The Hyperspell MCP server exposes your Hyperspell memories and tools to AI clients.

## Prerequisites

1. **Hyperspell API Key**: Set `HYPERSPELL_API_KEY` environment variable
2. **Hyperspell User ID**: Set `HYPERSPELL_USER_ID` environment variable (optional, defaults to sandbox account)
3. **Python 3.10+**: Required to run the MCP server

## Quick Start

### 1. Test the MCP Server

Run the MCP server directly to test:

```bash
cd backend
python services/hyperspell_mcp_server.py
```

Or use the start script:

```bash
cd backend
python start_mcp_server.py
```

The server communicates via stdio (standard input/output), which is how MCP clients connect to it.

### 2. Configure Claude Desktop

#### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hyperspell": {
      "command": "python",
      "args": ["/absolute/path/to/backend/services/hyperspell_mcp_server.py"],
      "env": {
        "HYPERSPELL_API_KEY": "Your_API_Key",
        "HYPERSPELL_USER_ID": "Your_User_ID"
      }
    }
  }
}
```

#### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hyperspell": {
      "command": "python",
      "args": ["C:\\absolute\\path\\to\\backend\\services\\hyperspell_mcp_server.py"],
      "env": {
        "HYPERSPELL_API_KEY": "Your_API_Key",
        "HYPERSPELL_USER_ID": "Your_User_ID"
      }
    }
  }
}
```

**Important**: Replace `/absolute/path/to/backend` with the actual absolute path to your backend directory.

### 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop. The MCP server will be available in Claude's tool list.

## Available Tools

The Hyperspell MCP server provides the following tools:

### 1. `search`
Search all memories indexed by Hyperspell.

**Parameters:**
- `query` (required): Search query to find relevant memories
- `answer` (optional, default: true): Whether to return an LLM-generated answer or just search results
- `max_results` (optional, default: 5): Maximum number of results to return

**Example:**
```json
{
  "query": "What did I learn about video marketing?",
  "answer": true,
  "max_results": 5
}
```

### 2. `add_memory`
Add text, markdown, or JSON to the Hyperspell index.

**Parameters:**
- `text` (required): Text, markdown, or JSON content to add
- `collection` (optional, default: "user_memories"): Collection name to organize memories

**Example:**
```json
{
  "text": "Video marketing tip: Use hooks in the first 3 seconds to capture attention.",
  "collection": "marketing_tips"
}
```

### 3. `get_memory`
Retrieve a memory by resource_id (not yet fully implemented).

**Parameters:**
- `resource_id` (required): Resource ID of the memory to retrieve

### 4. `upload_file`
Upload a file to the Hyperspell index.

**Parameters:**
- `file_path` (required): Path to the file to upload
- `collection` (optional, default: "user_documents"): Collection name

**Example:**
```json
{
  "file_path": "/path/to/document.pdf",
  "collection": "documents"
}
```

### 5. `list_integrations`
List all available integrations (requires additional Hyperspell API support).

### 6. `connect_integration`
Get a signed URL to connect to a given integration (requires additional Hyperspell API support).

### 7. `user_info`
Get basic info about the current user.

## Using with Other MCP Clients

The Hyperspell MCP server follows the standard MCP protocol and should work with any MCP-compatible client. Check your client's documentation for how to configure MCP servers.

Common clients:
- **Claude Desktop**: See configuration above
- **Cursor**: Check Cursor's MCP configuration documentation
- **Windsurf**: Check Windsurf's MCP configuration documentation

## Troubleshooting

### Server not starting

1. **Check environment variables:**
   ```bash
   echo $HYPERSPELL_API_KEY
   echo $HYPERSPELL_USER_ID
   ```

2. **Test Hyperspell service:**
   ```bash
   cd backend
   python -c "from services.hyperspell_service import HyperspellService; s = HyperspellService(); print('Available:', s.is_available())"
   ```

3. **Check Python path:**
   Make sure the `python` command in your config points to the correct Python interpreter (especially if using a virtual environment).

### Claude Desktop not connecting

1. **Check config file syntax**: Make sure the JSON is valid
2. **Use absolute paths**: Relative paths may not work
3. **Check logs**: Look for error messages in Claude Desktop's console/logs
4. **Restart Claude Desktop**: After changing config, fully quit and restart

### Tools not appearing

1. **Verify server is running**: The server should start automatically when Claude Desktop launches
2. **Check permissions**: Make sure the Python script is executable
3. **Test manually**: Run the server manually to see if there are any errors

## API Endpoint

You can also check MCP server information via the FastAPI endpoint:

```bash
GET /api/hyperspell/mcp/info
```

This returns configuration examples and setup instructions.

## Development

To modify the MCP server:

1. Edit `backend/services/hyperspell_mcp_server.py`
2. Test changes by running the server manually
3. Restart your MCP client to pick up changes

## References

- [Hyperspell MCP Documentation](https://docs.hyperspell.com/advanced/mcp-overview)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)








