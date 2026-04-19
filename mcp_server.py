# ── YouTube Content Creation Agent ───────────────────────────────────────────
# mcp_server.py — MCP Server via FastMCP
#
# Exposes the same core logic from app.py as MCP tools so that any
# MCP-compatible AI agent (e.g. Claude) can call them programmatically.
#
# MCP Tools exposed:
#   • get_latest_info_mcp  → wraps get_realtime_info()
#   • get_video_script_mcp → wraps generate_video_script()
#
# Run with:
#   python mcp_server.py
#
# Phase 1: Infrastructure & skeleton  ✅
# Phase 2: Core function implementation (coming next)
# ─────────────────────────────────────────────────────────────────────────────

# ── Standard library ─────────────────────────────────────────────────────────
import os

# ── Third-party: environment ──────────────────────────────────────────────────
from dotenv import load_dotenv

# ── Third-party: MCP framework ────────────────────────────────────────────────
from fastmcp import FastMCP

# ── Local: core logic (shared with app.py) ────────────────────────────────────
# Import the two core functions from app.py so we don't duplicate logic.
# Both the Streamlit UI and the MCP server share exactly one source of truth.
from app import get_realtime_info, generate_video_script


# ── 1. Load environment variables ─────────────────────────────────────────────
load_dotenv()


# ── 2. Initialise FastMCP server ──────────────────────────────────────────────
# The server name is displayed to MCP clients during tool discovery.
mcp = FastMCP("YouTube Content Creation Agent")


# ── 3. MCP Tool: get_latest_info_mcp ─────────────────────────────────────────

@mcp.tool()
def get_latest_info_mcp(query: str) -> str:
    """
    Fetch real-time web information on a given topic.

    This tool uses the Tavily Search API to retrieve recent, accurate
    information from the web on the topic provided. Use this before
    calling get_video_script_mcp to ensure the script is grounded in
    current facts.

    Args:
        query (str): The topic or search query to research.

    Returns:
        str: Formatted string of search results including titles, URLs,
             and content snippets relevant to the query.

    Example:
        get_latest_info_mcp("AI agents trends 2025")
    """
    return get_realtime_info(query)


# ── 4. MCP Tool: get_video_script_mcp ────────────────────────────────────────

@mcp.tool()
def get_video_script_mcp(info_text: str) -> str:
    """
    Generate a structured YouTube video script from research content.

    This tool takes the research text returned by get_latest_info_mcp
    and passes it to Google Gemini (gemini-2.0-flash) to produce a
    complete, production-ready YouTube video script.

    The generated script includes:
        - Hook (attention-grabbing opening)
        - Introduction (topic overview)
        - Main content sections (research-backed talking points)
        - Call to action (subscribe, like, comment prompts)
        - Outro

    Args:
        info_text (str): Research content, typically the output of
                         get_latest_info_mcp().

    Returns:
        str: A complete structured YouTube video script in markdown format.

    Example:
        info = get_latest_info_mcp("AI agents trends 2025")
        script = get_video_script_mcp(info)
    """
    return generate_video_script(info_text)


# ── 5. Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Starting YouTube Content Creation Agent MCP Server...")
    print("Tools available:")
    print("  • get_latest_info_mcp  — real-time topic research via Tavily")
    print("  • get_video_script_mcp — YouTube script generation via Gemini")
    print()
    mcp.run()