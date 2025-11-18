# FastMCP Cloud Deployment Guide

This guide explains how to deploy the Modus Docs MCP server to FastMCP Cloud.

## 🚀 Quick Deployment

### Step 1: Prerequisites
- GitHub account (https://github.com)
- Code already pushed to: https://github.com/ElishaSamPeterPrabhu/modus-docs

### Step 2: Deploy to FastMCP Cloud

1. **Visit FastMCP Cloud**: https://fastmcp.cloud
2. **Sign in** with your GitHub account
3. **Create a new project**:
   - Select repository: `ElishaSamPeterPrabhu/modus-docs`
   - Enter server entrypoint: `modus_docs_server.py:mcp`
   - Click "Deploy"

### Step 3: Get Your Server URL

After deployment, FastMCP Cloud will provide you with a URL like:
```
https://your-project.fastmcp.app/mcp
```

### Step 4: Configure MCP Client

Update your `~/.cursor/mcp.json` or Claude Desktop config with:

```json
{
  "mcpServers": {
    "modus-docs-hosted": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://your-project.fastmcp.app/mcp"
      ]
    }
  }
}
```

## 🧪 Testing Your Deployed Server

You can test your deployed server using the FastMCP Cloud chat interface or with a Python client:

```python
import asyncio
from fastmcp import Client

async def test_deployed_server():
    # Replace with your actual URL
    client = Client("https://your-project.fastmcp.app/mcp")
    
    async with client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")
        
        # Test a tool
        result = await client.call_tool("get_modus_component_data", {
            "component_name": "modus-wc-button"
        })
        print("✅ Server working!")

asyncio.run(test_deployed_server())
```

## 📋 Available Tools

Your deployed server exposes two tools:

### 1. `get_modus_implementation_data`
Fetches framework integration guides and general documentation.

**Available documents:**
- Framework Integration: `angular`, `react`, `vue`
- Guides: `getting-started`, `accessibility`, `form-inputs`, `modus-icon-usage`, `styling`, `testing`

**Example:**
```json
{
  "docs_name": "react"
}
```

### 2. `get_modus_component_data`
Fetches component-specific documentation for all 44+ Modus Web Components.

**Example:**
```json
{
  "component_name": "modus-wc-button"
}
```

**Special component:**
- `_all_components` - Returns catalog of all available components

## 🔧 Local Development

To run the server locally:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server
python3 modus_docs_server.py
```

Server will be available at: `http://localhost:8080/mcp`

## 🌐 Using Different Transports

### HTTP (for remote access)
```python
# Already configured in modus_docs_server.py
mcp.run(transport="http", host="0.0.0.0", port=8080)
```

### STDIO (for local MCP clients)
```python
mcp.run()  # Default is stdio
```

## 💡 FastMCP Cloud Features

- ✅ **Free for personal servers**
- ✅ **Automatic HTTPS**
- ✅ **Authentication support**
- ✅ **Easy GitHub integration**
- ✅ **Real-time logs and monitoring**

## 📚 Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [FastMCP Cloud](https://fastmcp.cloud)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [GitHub Repository](https://github.com/ElishaSamPeterPrabhu/modus-docs)

## 🆘 Troubleshooting

### Server not starting?
- Check that `requirements.txt` dependencies are installed
- Verify Python 3.8+ is being used
- Check logs in FastMCP Cloud dashboard

### Tools not working?
- Verify the `docs/` and `component-docs/` directories exist
- Check file permissions
- View server logs for errors

### Connection issues?
- Ensure the URL includes `/mcp` path
- Verify firewall settings (if self-hosting)
- Check that port 8080 is not already in use (local)

