# Kibana MCP Server

This project provides a Model Context Protocol (MCP) server implementation that allows AI assistants to interact with Kibana Security alerts.

## Features

This server exposes the following tools to MCP clients:

### Tools

*   **`tag_alert`**: Adds one or more tags to a specific Kibana security alert.
    *   `alert_id` (string, required): The ID of the Kibana alert to tag.
    *   `tags` (array of strings, required): A list of tags to add to the alert. Existing tags are preserved, and duplicates are handled.
*   **`adjust_alert_severity`**: Changes the severity of a specific Kibana security alert.
    *   `alert_id` (string, required): The ID of the Kibana alert.
    *   `new_severity` (string, required): The new severity level. Must be one of: "informational", "low", "medium", "high", "critical".

## Configuration

To connect to your Kibana instance, the server requires the following environment variables to be set:

*   `KIBANA_URL`: The base URL of your Kibana instance (e.g., `https://your-kibana.example.com:5601`).
*   `KIBANA_API_KEY`: Your Kibana API key in the format `id:secret`. Generate this in Kibana under Stack Management -> API Keys. Ensure the key has permissions to read and update alerts (e.g., appropriate privileges for the Alerting plugin).

## Quickstart

### Running the Server

Ensure you have set the required environment variables (`KIBANA_URL`, `KIBANA_API_KEY`). Then, navigate to the project directory and run the server using `uv`:

```bash
cd kibana-mcp
export KIBANA_URL="<your_kibana_url>"
export KIBANA_API_KEY="<your_api_key_id>:<your_api_key_secret>"
uv run kibana-mcp
```

The server will start and listen for MCP connections via standard input/output.

### Connecting a Client (e.g., Claude Desktop)

You can configure MCP clients like Claude Desktop to use this server.

**Claude Desktop Configuration:**

Edit your `claude_desktop_config.json` file:

*   macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
*   Windows: `%APPDATA%/Claude/claude_desktop_config.json`

Add the following server configuration under the `mcpServers` key, replacing `/path/to/kibana-mcp` with the actual absolute path to this project directory on your system:

```json
{
  "mcpServers": {
    "kibana-security": { // You can choose any name for the client to display
      "command": "uv",
      "args": [
        "run",
        "kibana-mcp"
      ],
      "options": {
          // Ensure the command runs within the correct project directory
          "cwd": "/path/to/kibana-mcp",
           // Pass required environment variables if not set globally
          "env": {
            "KIBANA_URL": "<your_kibana_url>",
            "KIBANA_API_KEY": "<your_api_key_id>:<your_api_key_secret>"
          }
      }
    }
  }
}
```

*(Note: Storing secrets directly in the config file is generally discouraged for production use. Consider more secure ways to manage environment variables if needed.)*

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

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command (replace `/path/to/kibana-mcp` with the actual project path):

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/kibana-mcp run kibana-mcp
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

## Local Development & Testing

To test this server locally, you can use the provided Docker Compose configuration located in the `testing/` directory to spin up local Elasticsearch and Kibana instances.

**Prerequisites:**

*   [Docker](https://docs.docker.com/get-docker/)
*   [Docker Compose](https://docs.docker.com/compose/install/)

**Quickstart:**

1.  Navigate to the `testing/` directory:
    ```bash
    cd testing
    ```
2.  Make the quickstart script executable (if you haven't already):
    ```bash
    chmod +x quickstart-test-env.sh
    ```
3.  Run the quickstart script:
    ```bash
    ./quickstart-test-env.sh
    ```
4.  The script will start the containers and print the access URLs and credentials.
5.  Remember to navigate back to the root directory (`cd ..`) before running the MCP server.

**Manual Setup Steps (if not using the script):**

1.  **Check Passwords:**
    *   Open the `testing/docker-compose.yml` file.
    *   The default password for the `elastic` user is set to `elastic`. You can change this if needed (ensure it's the same for both services and update the healthcheck).
    *   **Warning:** Do not use the default password in a production environment.
    *   *(Optional)*: Handle persistent volumes as needed within `testing/docker-compose.yml`.

2.  **Start Services:**
    *   Navigate to the `testing/` directory.
    *   Run the command:
        ```bash
        # Use 'docker compose' if you have v2
        docker compose -f docker-compose.yml up -d
        # Or 'docker-compose' if you have v1
        # docker-compose -f docker-compose.yml up -d
        ```

3.  **Access Services:**
    *   **Elasticsearch:** `http://localhost:9200` (or the port defined in `testing/docker-compose.yml`)
    *   **Kibana:** `http://localhost:5601` (or the port defined in `testing/docker-compose.yml`)
    *   Login using username `elastic` and the password from `testing/docker-compose.yml`.

4.  **Configure MCP Server:**
    *   Set the environment variables **before** running the server script (from the **root** directory):
        *   `KIBANA_URL=http://localhost:5601`
        *   Set `KIBANA_API_KEY` **or** (`KIBANA_USERNAME` and `KIBANA_PASSWORD`). For the local setup, use:
            *   `KIBANA_USERNAME=elastic`
            *   `KIBANA_PASSWORD=elastic`

5.  **Run the Server:**
    *   From the **root** directory:
        ```bash
        export KIBANA_URL=http://localhost:5601
        export KIBANA_USERNAME=elastic
        export KIBANA_PASSWORD=elastic
        # Or export KIBANA_API_KEY=...

        # Assuming your package/module is runnable
        python -m src.kibana_mcp.server
        ```

6.  **Testing:**
    *   Send requests to your MCP server (stdin/stdout).

7.  **Stop Services:**
    *   Navigate to the `testing/` directory.
    *   Run:
        ```bash
        docker compose -f docker-compose.yml down
        # Or
        # docker-compose -f docker-compose.yml down
        ```

## Running the Server

Set the required environment variables (`KIBANA_URL` and authentication variables) as described above.

Then, from the **root** directory, run the server module:

```bash
# Example:
pip install -r requirements.txt # If you have one

export KIBANA_URL=http://your-kibana-instance:5601
export KIBANA_API_KEY="YOUR_BASE64_ENCODED_API_KEY"
# Or:
# export KIBANA_USERNAME=your_user
# export KIBANA_PASSWORD=your_pass

python -m src.kibana_mcp.server
```

## Available Tools

*   `tag_alert`: Adds tags to a Kibana security alert.
*   `adjust_alert_severity`: Changes the severity of a Kibana security alert.
*   `get_alerts`: Fetches recent Kibana security alerts.