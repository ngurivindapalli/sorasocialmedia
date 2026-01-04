# How to Use Hyperspell MCP Server

This guide explains how to use the Hyperspell MCP (Model Context Protocol) server with AI clients like Claude Desktop.

## What is MCP?

MCP (Model Context Protocol) allows AI applications like Claude Desktop to connect to external data sources and tools. Our Hyperspell MCP server gives Claude access to your Hyperspell memories, so Claude can search, add, and retrieve information from your memory layer.

## Step 1: Verify Setup

First, make sure your Hyperspell service is configured:

```bash
# Check environment variables
echo $HYPERSPELL_API_KEY
echo $HYPERSPELL_USER_ID
```

If not set, add them to your `.env` file in the backend directory:
```
HYPERSPELL_API_KEY=your_api_key_here
HYPERSPELL_USER_ID=your_user_id_here
```

## Step 2: Test the MCP Server

Test that the MCP server works:

```bash
cd backend
python services/hyperspell_mcp_server.py
```

The server should start and wait for input. Press Ctrl+C to stop it. If it starts without errors, you're good to go!

## Step 3: Configure Claude Desktop

### macOS Configuration

1. **Find your backend path:**
   ```bash
   cd backend
   pwd
   # Copy this full path
   ```

2. **Open Claude Desktop config:**
   ```bash
   open ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

   If the file doesn't exist, create it:
   ```bash
   mkdir -p ~/Library/Application\ Support/Claude
   touch ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

3. **Add MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "hyperspell": {
         "command": "python",
         "args": ["/Users/YourUsername/path/to/backend/services/hyperspell_mcp_server.py"],
         "env": {
           "HYPERSPELL_API_KEY": "your_api_key_here",
           "HYPERSPELL_USER_ID": "your_user_id_here"
         }
       }
     }
   }
   ```

   **Important:** Replace `/Users/YourUsername/path/to/backend` with the actual absolute path from step 1.

### Windows Configuration

1. **Find your backend path:**
   ```powershell
   cd backend
   pwd
   # Copy this full path
   ```

2. **Open Claude Desktop config:**
   - Press `Win + R`
   - Type: `%APPDATA%\Claude\claude_desktop_config.json`
   - Press Enter

   If the file doesn't exist, create the directory and file:
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude"
   New-Item -ItemType File -Force -Path "$env:APPDATA\Claude\claude_desktop_config.json"
   ```

3. **Add MCP server configuration:**
   ```json
   {
     "mcpServers": {
       "hyperspell": {
         "command": "python",
         "args": ["C:\\Users\\YourUsername\\path\\to\\backend\\services\\hyperspell_mcp_server.py"],
         "env": {
           "HYPERSPELL_API_KEY": "your_api_key_here",
           "HYPERSPELL_USER_ID": "your_user_id_here"
         }
       }
     }
   }
   ```

   **Important:** 
   - Replace `C:\\Users\\YourUsername\\path\\to\\backend` with your actual absolute path
   - Use double backslashes `\\` in Windows paths
   - Make sure `python` is in your PATH, or use the full path to Python

### Using Python from Virtual Environment

If you're using a virtual environment, use the full path to the Python executable:

**macOS:**
```json
{
  "mcpServers": {
    "hyperspell": {
      "command": "/Users/YourUsername/path/to/backend/venv/bin/python",
      "args": ["/Users/YourUsername/path/to/backend/services/hyperspell_mcp_server.py"],
      "env": {
        "HYPERSPELL_API_KEY": "your_api_key_here",
        "HYPERSPELL_USER_ID": "your_user_id_here"
      }
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "hyperspell": {
      "command": "C:\\Users\\YourUsername\\path\\to\\backend\\venv\\Scripts\\python.exe",
      "args": ["C:\\Users\\YourUsername\\path\\to\\backend\\services\\hyperspell_mcp_server.py"],
      "env": {
        "HYPERSPELL_API_KEY": "your_api_key_here",
        "HYPERSPELL_USER_ID": "your_user_id_here"
      }
    }
  }
}
```

## Step 4: Restart Claude Desktop

After saving the config file:
1. **Completely quit Claude Desktop** (not just close the window)
2. **Restart Claude Desktop**
3. The MCP server should automatically start when Claude launches

## Step 5: Verify MCP is Working

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Check for MCP tools**: You should see Hyperspell tools available in Claude's tool list
4. **Test with a query**: Try asking Claude:
   - "Search my Hyperspell memories for information about video marketing"
   - "What memories do I have about content creation?"

## Available Tools in Claude

Once configured, Claude will have access to these tools:

### 1. **search** - Search Memories
Ask Claude to search your memories:
- "Search my Hyperspell memories for [topic]"
- "What do I know about [subject]?"
- "Find memories related to [keyword]"

### 2. **add_memory** - Add New Memories
Ask Claude to save information:
- "Add this to my Hyperspell memory: [text]"
- "Remember that [information]"
- "Save this to my memory: [content]"

### 3. **upload_file** - Upload Files
Ask Claude to upload files:
- "Upload this file to Hyperspell: [file path]"
- "Add this document to my memory: [file path]"

### 4. **user_info** - Get User Info
Ask Claude about your account:
- "What's my Hyperspell user info?"
- "Show me my Hyperspell account details"

## Example Conversations

### Example 1: Searching Memories
```
You: Search my Hyperspell memories for information about Instagram video analysis

Claude: [Uses search tool]
I found the following memories about Instagram video analysis:
- Memory 1: "Instagram videos should have hooks in the first 3 seconds..."
- Memory 2: "Top performing videos use trending audio..."
```

### Example 2: Adding a Memory
```
You: Remember that I prefer videos between 15-30 seconds for LinkedIn

Claude: [Uses add_memory tool]
I've saved that to your Hyperspell memory. Your preference for 15-30 second LinkedIn videos is now stored.
```

### Example 3: Combining Search and Context
```
You: Based on my previous memories, what should I know about video content strategy?

Claude: [Uses search tool, then provides context]
Based on your memories, here's what you've learned about video content strategy:
1. Hook viewers in the first 3 seconds
2. Use trending audio for better reach
3. Post consistently for algorithm favor
...
```

## Troubleshooting

### MCP Server Not Appearing in Claude

1. **Check config file syntax:**
   - Make sure JSON is valid (use a JSON validator)
   - Check for trailing commas
   - Verify all quotes are properly escaped

2. **Verify Python path:**
   ```bash
   # Test if Python works
   python --version
   
   # Test the MCP server directly
   python backend/services/hyperspell_mcp_server.py
   ```

3. **Check Claude Desktop logs:**
   - Look for error messages in Claude's console
   - On macOS: Check Console.app for Claude errors
   - On Windows: Check Event Viewer

4. **Verify environment variables:**
   - Make sure `HYPERSPELL_API_KEY` is set correctly
   - Make sure `HYPERSPELL_USER_ID` is set correctly

### Tools Not Working

1. **Test Hyperspell service:**
   ```bash
   cd backend
   python -c "from services.hyperspell_service import HyperspellService; s = HyperspellService(); print('Available:', s.is_available())"
   ```

2. **Check API endpoint:**
   ```bash
   curl http://localhost:8000/api/hyperspell/status
   ```

3. **Verify MCP server info:**
   ```bash
   curl http://localhost:8000/api/hyperspell/mcp/info
   ```

### Permission Errors

If you get permission errors:
```bash
# Make the script executable (macOS/Linux)
chmod +x backend/services/hyperspell_mcp_server.py

# Or use Python explicitly
python backend/services/hyperspell_mcp_server.py
```

## Getting Help

1. **Check the setup guide:** `backend/HYPERSPELL_MCP_SETUP.md`
2. **Test the server manually:** Run it directly to see error messages
3. **Check API status:** Visit `http://localhost:8000/api/hyperspell/mcp/info`
4. **Review logs:** Check backend console for error messages

## Next Steps

Once MCP is working:

1. **Start using it regularly:** Ask Claude to search your memories when working on projects
2. **Build your memory layer:** Add important information as you work
3. **Organize with collections:** Use different collections for different topics
4. **Integrate with your workflow:** Use Claude + Hyperspell for better context-aware assistance

## Quick Reference

**Config File Locations:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Test Command:**
```bash
python backend/services/hyperspell_mcp_server.py
```

**API Endpoints:**
- Status: `GET /api/hyperspell/status`
- MCP Info: `GET /api/hyperspell/mcp/info`

**Environment Variables:**
- `HYPERSPELL_API_KEY` - Your Hyperspell API key
- `HYPERSPELL_USER_ID` - Your Hyperspell user ID (optional)











