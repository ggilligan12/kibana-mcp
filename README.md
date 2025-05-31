[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ggilligan12-kibana-mcp-badge.png)](https://mseep.ai/app/ggilligan12-kibana-mcp)

# Kibana MCP Server

![Kibana MCP Demo](faster-server-demo.gif)

Model Context Protocol (MCP) server for Kibana Security - manage alerts, rules, and exceptions via AI assistants.

## Quick Start

### 1. Clone and Build
```bash
git clone https://github.com/ggilligan12/kibana-mcp.git
cd kibana-mcp
docker build -t kibana-mcp .
```

### 2. Configure MCP Client
Add to your MCP client config (Claude Desktop, Cursor, etc.):

**Option A: Using Environment Variables (Recommended)**

First, set your credentials:
```bash
export KIBANA_URL="https://your-kibana.example.com:5601"

# Option 1: API Key (recommended)
export KIBANA_API_KEY="your_base64_api_key"

# Option 2: Username/Password
# export KIBANA_USERNAME="your_username"
# export KIBANA_PASSWORD="your_password"
```

Then add to your MCP config:
```json
{
  "mcpServers": {
    "kibana-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--network", "host", "-e", "KIBANA_URL", "-e", "KIBANA_API_KEY", "kibana-mcp"]
    }
  }
}
```

For username/password, use:
```json
{
  "mcpServers": {
    "kibana-mcp": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--network", "host", "-e", "KIBANA_URL", "-e", "KIBANA_USERNAME", "-e", "KIBANA_PASSWORD", "kibana-mcp"]
    }
  }
}
```

**Option B: Direct Credentials (Easier for Claude Desktop)**

Using API Key:
```json
{
  "mcpServers": {
    "kibana-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--network", "host",
        "-e", "KIBANA_URL=https://your-kibana.example.com:5601",
        "-e", "KIBANA_API_KEY=your_base64_api_key",
        "kibana-mcp"
      ]
    }
  }
}
```

Using Username/Password:
```json
{
  "mcpServers": {
    "kibana-mcp": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm", "--network", "host",
        "-e", "KIBANA_URL=https://your-kibana.example.com:5601",
        "-e", "KIBANA_USERNAME=your_username",
        "-e", "KIBANA_PASSWORD=your_password",
        "kibana-mcp"
      ]
    }
  }
}
```

*Note: Option B is less secure but more convenient for tools like Claude Desktop where environment variables are harder to manage.*

## Available Tools

- **`get_alerts`** - Fetch security alerts
- **`tag_alert`** - Add tags to alerts  
- **`adjust_alert_status`** - Change alert status (open/acknowledged/closed)
- **`find_rules`** - Search detection rules
- **`get_rule_exceptions`** - Get rule exception items
- **`add_rule_exception_items`** - Add exceptions to rules
- **`create_exception_list`** - Create new exception lists
- **`associate_shared_exception_list`** - Link exception lists to rules

## Local Development

```bash
# Install dependencies
uv sync

# Set environment variables (see above)

# Run locally
uv run kibana-mcp
```

### Test Environment
```bash
# Start local Kibana/Elasticsearch with test data
pip install -r testing/requirements-dev.txt
./testing/quickstart-test-env.sh

# Access at http://localhost:5601 (elastic/elastic)
```

