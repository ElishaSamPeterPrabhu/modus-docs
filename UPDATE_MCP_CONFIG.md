# Update MCP Configuration with Authentication

Your FastMCP Cloud server is deployed at:
**https://clumsy-amaranth-stork.fastmcp.app/mcp**

## 🔐 Authentication Required

The server requires authentication (401 Unauthorized error). Follow these steps:

### Step 1: Get Your API Token

1. Visit **https://fastmcp.cloud**
2. Sign in and go to your project dashboard
3. Find the **API Keys** or **Authentication** section
4. Copy your authentication token

### Step 2: Update Your `~/.cursor/mcp.json`

Replace the current `modus-docs-hosted` configuration with:

```json
"modus-docs-hosted": {
  "command": "npx",
  "args": [
    "-y",
    "mcp-remote",
    "https://clumsy-amaranth-stork.fastmcp.app/mcp",
    "--header",
    "Authorization: Bearer ${FASTMCP_TOKEN}"
  ],
  "env": {
    "FASTMCP_TOKEN": "YOUR_TOKEN_HERE"
  }
}
```

### Step 3: Alternative - Make Server Public (if available)

If FastMCP Cloud allows public servers, you can:
1. Go to your project settings in FastMCP Cloud
2. Look for "Access Control" or "Public Access"
3. Enable public access (no authentication required)

## 🧪 Testing After Configuration

Once you've added the token, restart Cursor and test by asking:
```
"Can you list the available Modus components?"
```

The AI should be able to use the `get_modus_component_data` and `get_modus_implementation_data` tools.

## 📝 Current Configuration

Your current `~/.cursor/mcp.json` has:
- ✅ `modus-docs-local` - Local server (STDIO)
- ✅ `modus-docs-hosted` - FastMCP Cloud server (needs auth token)

## 💡 Quick Test with Python

To test with the authentication token:

```python
import asyncio
from fastmcp import Client

async def test():
    # Add your token here
    client = Client(
        "https://clumsy-amaranth-stork.fastmcp.app/mcp",
        headers={"Authorization": "Bearer YOUR_TOKEN_HERE"}
    )
    
    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

asyncio.run(test())
```

## 🆘 Troubleshooting

### Still getting 401 errors?
- Verify the token is correct
- Check token hasn't expired
- Make sure Bearer prefix is included
- Restart Cursor after config changes

### Can't find API keys in dashboard?
- Check FastMCP Cloud documentation
- Look for "Settings" → "API Keys"
- Contact FastMCP Cloud support

## 📚 Resources

- [FastMCP Cloud Dashboard](https://fastmcp.cloud)
- [FastMCP Documentation](https://gofastmcp.com)
- [Your GitHub Repo](https://github.com/ElishaSamPeterPrabhu/modus-docs)

