import asyncio
import os
import httpx
from typing import List, Optional, Dict
import logging

# Import FastMCP and types
from fastmcp import FastMCP
import mcp.types as types

# Import handler implementations using absolute paths
from kibana_mcp.tools import (_call_tag_alert, _call_adjust_alert_status, _call_get_alerts, 
                          execute_tool_safely)
from kibana_mcp.resources import handle_read_resource
from kibana_mcp.prompts import handle_get_prompt

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("kibana-mcp")

# --- Global MCP Instance and HTTP Client ---
logger.info("Initializing Kibana MCP Server (FastMCP)...")
mcp = FastMCP("kibana-mcp")
http_client: httpx.AsyncClient | None = None

def configure_http_client():
    """Configure the global httpx client using environment variables."""
    global http_client
    kibana_url = os.getenv("KIBANA_URL")
    encoded_api_key = os.getenv("KIBANA_API_KEY")
    kibana_username = os.getenv("KIBANA_USERNAME")
    kibana_password = os.getenv("KIBANA_PASSWORD")

    if not kibana_url:
        logger.error("KIBANA_URL environment variable not set.")
        raise ValueError("KIBANA_URL environment variable not set.")

    headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}
    auth_config = {}
    auth_method_used = "None"

    if encoded_api_key:
        logger.info("Configuring authentication using API Key.")
        auth_header = encoded_api_key if encoded_api_key.strip().startswith("ApiKey ") else f"ApiKey {encoded_api_key.strip()}"
        headers["Authorization"] = auth_header
        auth_method_used = "API Key"
    elif kibana_username and kibana_password:
        logger.info(f"Configuring authentication using Basic auth for user: {kibana_username}")
        auth_config["auth"] = (kibana_username, kibana_password)
        auth_method_used = "Username/Password"
    else:
        logger.error("Kibana authentication not configured.")
        raise ValueError("Kibana authentication not configured. Set KIBANA_API_KEY or both KIBANA_USERNAME/PASSWORD.")

    logger.info(f"Creating HTTP client for Kibana at {kibana_url} using {auth_method_used}.")
    http_client = httpx.AsyncClient(
        base_url=kibana_url, headers=headers, timeout=30.0, verify=False, **auth_config
    )

async def close_http_client():
    """Close the global httpx client."""
    global http_client
    if http_client:
        logger.info("Closing HTTP client...")
        await http_client.aclose()
        http_client = None
        logger.info("HTTP client closed.")

# --- Handler Functions with FastMCP Decorators ---

# NOTE: list_* handlers might need specific registration if not automatic

@mcp.resource("alert://{alert_id}")
async def read_alert_resource(alert_id: str) -> str:
    uri = f"alert://{alert_id}"
    logger.info(f"Handling read_resource for URI: {uri}")
    return await handle_read_resource(uri=uri)

@mcp.prompt("prompt://{prompt_name}")
async def get_kibana_prompt(prompt_name: str) -> types.GetPromptResult:
    uri = f"prompt://{prompt_name}"
    logger.info(f"Handling get_prompt for URI: {uri}")
    return await handle_get_prompt(uri=uri)

# --- Individual Tool Handlers ---

@mcp.tool()
async def tag_alert(alert_id: str, tags: List[str]) -> list[types.TextContent]:
    """Adds one or more tags to a specific Kibana security alert signal."""
    # Delegate execution to the safe wrapper
    return await execute_tool_safely(
        tool_name='tag_alert',
        tool_impl_func=_call_tag_alert,
        http_client=http_client,
        alert_id=alert_id, 
        tags_to_add=tags # Pass correct arg name expected by _call_tag_alert
    )

@mcp.tool()
async def adjust_alert_status(alert_id: str, new_status: str) -> list[types.TextContent]:
    """Changes the status of a specific Kibana security alert signal."""
    # Basic validation remains here as it's specific to this tool's input
    valid_statuses = ["open", "acknowledged", "closed"]
    if new_status not in valid_statuses:
         err_msg = f"Invalid status '{new_status}'. Must be one of {valid_statuses}."
         logger.warning(f"Tool 'adjust_alert_status' called with invalid status for alert {alert_id}: {new_status}")
         return [types.TextContent(type="text", text=err_msg)]

    # Delegate execution to the safe wrapper
    return await execute_tool_safely(
        tool_name='adjust_alert_status',
        tool_impl_func=_call_adjust_alert_status,
        http_client=http_client,
        alert_id=alert_id, 
        new_status=new_status
    )

@mcp.tool()
async def get_alerts(limit: int = 20, 
                     search_text: str = "*"
                     ) -> list[types.TextContent]:
    """Fetches recent Kibana security alert signals, optionally filtering by text and limiting quantity."""
    # Delegate execution to the safe wrapper, extracting values from the args model
    return await execute_tool_safely(
        tool_name='get_alerts',
        tool_impl_func=_call_get_alerts,
        http_client=http_client,
        limit=limit, 
        search_text=search_text
    )

def run_server():
    """Configure client, run the MCP server loop, and handle cleanup."""
    global http_client # Need global to ensure cleanup happens
    http_client = None # Ensure it's None initially
    try:
        configure_http_client() # Configure global client
        logger.info(f"Starting FastMCP server run loop...")
        # Call the synchronous run method, which handles the event loop
        mcp.run()
        logger.info(f"FastMCP server run loop finished normally.")
    except Exception as e:
        logger.error(f"Error during server run: {e}", exc_info=True)
    finally:
        logger.info("Shutting down server...")
        # Need to run the async close in a temporary event loop
        if http_client:
            try:
                # Create a new loop *just* for closing the client if run finished/errored
                asyncio.run(close_http_client())
            except RuntimeError as re:
                # Handle case where loop might already be closed or another issue
                logger.error(f"Error closing HTTP client in finally block: {re}", exc_info=True)
        else:
             logger.info("HTTP client was not initialized or already closed.")

# Allows running the server directly using `python -m kibana_mcp` or `uv run kibana-mcp`
if __name__ == "__main__":
    run_server() # Call the synchronous function directly