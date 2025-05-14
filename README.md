[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ggilligan12-kibana-mcp-badge.png)](https://mseep.ai/app/ggilligan12-kibana-mcp)

# Kibana MCP Server

![Kibana MCP Demo](faster-server-demo.gif)

This project provides a Model Context Protocol (MCP) server implementation that allows AI assistants to interact with Kibana Security functions, including alerts, rules, and exceptions.

## Features

This server exposes the following tools to MCP clients:

### Tools

*   **`tag_alert`**: Adds one or more tags to a specific Kibana security alert signal.
    *   `alert_id` (string, required): The ID of the Kibana alert signal to tag.
    *   `tags` (array of strings, required): A list of tags to add to the alert signal.
*   **`adjust_alert_status`**: Changes the status of a specific Kibana security alert signal.
    *   `alert_id` (string, required): The ID of the Kibana alert signal.
    *   `new_status` (string, required): The new status. Must be one of: "open", "acknowledged", "closed".
*   **`get_alerts`**: Fetches recent Kibana security alert signals, optionally filtering by text and limiting quantity.
    *   `limit` (integer, optional, default: 20): Maximum number of alerts to return.
    *   `search_text` (string, optional, default: "*"): Text to search for across various alert fields (name, reason, description, host, user, etc.).
*   **`get_rule_exceptions`**: Retrieves the exception items associated with a specific detection rule.
    *   `rule_id` (string, required): The internal UUID of the detection rule.
*   **`add_rule_exception_items`**: Adds one or more exception items to a specific detection rule's exception list. (Note: This implicitly creates a `rule_default` exception list if one doesn't exist, or adds to the existing one. It also requires the rule's internal UUID, not the human-readable `rule_id`.)
    *   `rule_id` (string, required): The internal UUID of the detection rule to add exceptions to.
    *   `items` (array of objects, required): A list of exception item objects to add. Each object should contain fields like `description`, `entries` (list of match conditions), `item_id`, `name`, `type`, etc., but **omit** the `list_id` field.
*   **`create_exception_list`**: Creates a new exception list container.
    *   `list_id` (string, required): Human-readable identifier for the list (e.g., 'trusted-ips').
    *   `name` (string, required): Display name for the exception list.
    *   `description` (string, required): Description of the list's purpose.
    *   `type` (string, required): Type of list ('detection', 'endpoint', etc.).
    *   `namespace_type` (string, optional, default: 'single'): Scope ('single' or 'agnostic').
    *   `tags` (array of strings, optional): List of tags.
    *   `os_types` (array of strings, optional): List of OS types ('linux', 'macos', 'windows').
*   **`associate_shared_exception_list`**: Associates an existing shared exception list (not a rule default) with a detection rule.
    *   `rule_id` (string, required): The human-readable `rule_id` of the detection rule.
    *   `exception_list_id` (string, required): The human-readable `list_id` of the shared exception list to associate.
    *   `exception_list_type` (string, optional, default: 'detection'): The type of the exception list.
    *   `exception_list_namespace` (string, optional, default: 'single'): The namespace type of the exception list.
*   **`find_rules`**: Finds detection rules, optionally filtering by KQL/Lucene, sorting, and paginating. (Note: Passing optional parameters like `filter` or `per_page` may encounter issues depending on the MCP client/framework version).
    *   `filter` (string, optional): KQL or Lucene query string to filter rules.
    *   `sort_field` (string, optional): Field to sort rules by (e.g., 'name', 'updated_at').
    *   `sort_order` (string, optional): Sort order ('asc' or 'desc').
    *   `page` (integer, optional): Page number for pagination (1-based).
    *   `per_page` (integer, optional): Number of rules per page.

## Configuration

To connect to your Kibana instance, the server requires the following environment variables to be set:

*   `KIBANA_URL`: The base URL of your Kibana instance (e.g., `https://your-kibana.example.com:5601`).

And **one** of the following authentication methods:

*   **API Key (Recommended):**
    *   `KIBANA_API_KEY`: A Base64 encoded Kibana API key. Generate this in Kibana under Stack Management -> API Keys. Ensure the key has permissions to read and update security alerts/signals (e.g., appropriate privileges for the Security Solution feature).
    *   Example format: `VzR1dU5COXdPUTRhQVZHRWw2bkk6LXFSZGRIVGNRVlN6TDA0bER4Z1JxUQ==` (This is just an example, use your actual key).
*   **Username/Password (Less Secure):**
    *   `KIBANA_USERNAME`: Your Kibana username.
    *   `KIBANA_PASSWORD`: Your Kibana password.

The server prioritizes `KIBANA_API_KEY` if it is set. If it's not set, it will attempt to use `KIBANA_USERNAME` and `KIBANA_PASSWORD`.

## Quickstart: Running the Server

1.  Set the required environment variables (`KIBANA_URL` and authentication variables).

    *   **Using API Key:**
        ```bash
        export KIBANA_URL="<your_kibana_url>"
        export KIBANA_API_KEY="<your_base64_encoded_api_key>"
        ```
    *   **Using Username/Password:**
        ```bash
        export KIBANA_URL="<your_kibana_url>"
        export KIBANA_USERNAME="<your_kibana_username>"
        export KIBANA_PASSWORD="<your_kibana_password>"
        ```

2.  Navigate to the project directory (`kibana-mcp`).
3.  Run the server using `uv` (which uses the entry point defined in `pyproject.toml`):

    ```bash
    uv run kibana-mcp
    ```

The server will start and listen for MCP connections via standard input/output.

## Connecting an MCP Client (e.g., Cursor, Claude Desktop)

You can configure MCP clients like Cursor or Claude Desktop to use this server.

**Configuration File Locations:**

*   Cursor: `~/.cursor/mcp.json`
*   Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows)

Add the following server configuration under the `mcpServers` key, replacing `/path/to/kibana-mcp` with the actual absolute path to your project root. Choose **one** authentication method (`KIBANA_API_KEY` or `KIBANA_USERNAME`/`KIBANA_PASSWORD`) within the command arguments.

**Recommended Configuration (using `/usr/bin/env`):**

Some client applications may not reliably pass environment variables defined in their configuration's `env` block. Using `/usr/bin/env` directly ensures the variables are set for the server process.

```json
{
  "mcpServers": {
    "kibana-mcp": { // You can choose any name for the client to display
      "command": "/usr/bin/env", // Use env command for reliability
      "args": [
        // Set required environment variables here
        "KIBANA_URL=<your_kibana_url>",

        // Option 1: API Key (Recommended)
        "KIBANA_API_KEY=<your_base64_encoded_api_key>",

        // Option 2: Username/Password (Mutually exclusive with API Key)
        // "KIBANA_USERNAME=<your_kibana_username>",
        // "KIBANA_PASSWORD=<your_kibana_password>",

        // Command to run the server (using absolute paths)
        "/path/to/your/virtualenv/bin/python", // e.g., /Users/me/kibana-mcp/.venv/bin/python
        "/path/to/kibana-mcp/src/kibana_mcp/server.py" // Absolute path to server script
      ],
      "options": {
          "cwd": "/path/to/kibana-mcp" // Set correct working directory
          // No "env" block needed here when using /usr/bin/env in command/args
      }
    }
    // Add other servers here if needed
  }
}
```

*(Note: Replace placeholders like `<your_kibana_url>`, `<your_base64_encoded_api_key>`, and the python/script paths with your actual values. Storing secrets directly in the config file is generally discouraged for production use. Consider more secure ways to manage environment variables if needed.)*

**Alternative Configuration (Standard `env` block - might not work reliably):**

*(This is the standard documented approach but proved unreliable in some environments)*

```json
{
  "mcpServers": {
    "kibana-mcp-alt": { 
      "command": "/path/to/your/virtualenv/bin/python", 
      "args": [
        "/path/to/kibana-mcp/src/kibana_mcp/server.py"
      ],
      "options": {
          "cwd": "/path/to/kibana-mcp",
          // Choose one auth method:
          "KIBANA_API_KEY": "<your_base64_encoded_api_key>"
          // OR
          // "KIBANA_USERNAME": "<your_kibana_username>",
          // "KIBANA_PASSWORD": "<your_kibana_password>"
      }
    }
  }
}
```

## Development

### Installing Dependencies

Sync dependencies using `uv`:

```bash
uv sync
```

### Building and Publishing

To prepare the package for distribution:

1.  Build package distributions:
    ```bash
    uv build
    ```
    This will create source and wheel distributions in the `dist/` directory.

2.  Publish to PyPI:
    ```bash
    uv publish
    ```
    Note: You'll need to configure PyPI credentials.

## Local Development & Testing Environment

The `testing/` directory contains scripts and configuration to spin up local Elasticsearch and Kibana instances using Docker Compose and automatically seed them with a sample detection rule.

**Prerequisites:**

*   [Python 3](https://www.python.org/)
*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)
*   Python dependencies for testing scripts: Install using
    ```bash
    pip install -r requirements-dev.txt
    ```

**Quickstart:**

1.  Install development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```
2.  Run the quickstart script from the project root directory:
    ```bash
    ./testing/quickstart-test-env.sh
    ```
3.  The script (`testing/main.py`) will perform checks, start the containers, wait for services, create a sample **detection rule**, write sample auth data, verify signal generation, and print the access URLs/credentials.
4.  Access Kibana at `http://localhost:5601` (User: `elastic`, Pass: `elastic`). The internal user Kibana connects with is `kibana_system_user`.

**Manual Steps (Overview):**

The `testing/quickstart-test-env.sh` script executes `python -m testing.main`. This Python script performs the following:
1.  Checks for Docker & Docker Compose.
2.  Parses `testing/docker-compose.yml` for configuration.
3.  Runs `docker compose up -d`.
4.  Waits for Elasticsearch and Kibana APIs.
5.  Creates a custom user (`kibana_system_user`) and role for Kibana's internal use.
6.  Creates an index template (`mcp_auth_logs_template`).
7.  Reads `testing/sample_rule.json` (a detection rule).
8.  Sends a POST request to `http://localhost:5601/api/detection_engine/rules` to create the rule.
9.  Writes sample data from `testing/auth_events.ndjson` to `mcp-auth-logs-default` index.
10. Checks for detection signals using `http://localhost:5601/api/detection_engine/signals/search`.
11. Prints status, URLs, credentials, and shutdown commands.

**Stopping the Test Environment:**

*   Run the shutdown command printed by the script (e.g., `docker compose -f testing/docker-compose.yml down`). Use the `-v` flag (`down -v`) to remove data volumes if needed.