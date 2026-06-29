# researcher.py
# This module defines the Research Agent for the InfoQuant system using Google ADK.
#
# Day 2 Change: The Research Agent now uses the official remote Google Developer
# Knowledge MCP server. The configuration is loaded dynamically from the global
# mcp_config.json file to avoid hardcoding API keys in the source code.

import os
import sys
import json
from google.adk import Agent
from google.adk.tools import McpToolset
from google.adk.tools.mcp_tool.mcp_toolset import StreamableHTTPConnectionParams

# ---------------------------------------------------------------------------
# Dynamic MCP Configuration Loader
#
# Loads server connection URL and API key dynamically from the globally
# configured config file at ~/.gemini/config/mcp_config.json.
# ---------------------------------------------------------------------------
config_path = os.path.join(os.path.expanduser("~"), ".gemini", "config", "mcp_config.json")
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Global MCP configuration file not found at: {config_path}")

with open(config_path) as f:
    mcp_config = json.load(f)

# Extract config for google-developer-knowledge
gdk_config = mcp_config.get("mcpServers", {}).get("google-developer-knowledge")
if not gdk_config:
    raise KeyError("google-developer-knowledge MCP server config not found in mcp_config.json")

server_url = gdk_config.get("serverUrl")
headers = gdk_config.get("headers", {})

# Initialize McpToolset with remote parameters loaded from the configuration file
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=server_url,
        headers=headers
    )
)

# Define the Research Agent with MCP tools attached
research_agent = Agent(
    name="research_agent",
    model="gemini-2.5-flash",
    instruction=(
        "You are a Research Agent for InfoQuant. "
        "Your task is to gather information on the requested topic and return "
        "ONLY concise, structured notes under 300 words.\n\n"
        "IMPORTANT — Use MCP tools in this order:\n"
        "1. Call search_documents(query) with the topic as the query. "
        "   This searches Google Developer documentation.\n"
        "2. If the snippets are insufficient, call get_documents(names) "
        "   to fetch full content.\n"
        "3. Use what you find from the MCP tools to write your notes. "
        "   If the tools return no useful results, use your model knowledge.\n\n"
        "Your notes MUST include:\n"
        "- What it is\n"
        "- Key concepts\n"
        "- Real-world applications\n"
    ),
    tools=[mcp_toolset],  # Attach the MCP toolset — ADK handles the connection
)
