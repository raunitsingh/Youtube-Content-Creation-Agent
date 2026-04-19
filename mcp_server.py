# Run: python mcp_server.py

import os

from dotenv import load_dotenv
from fastmcp import FastMCP

# Import core functions from app.py — single source of truth, no duplication
from app import get_realtime_info, generate_video_script


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

mcp = FastMCP("YouTube Content Creation Agent")


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def get_latest_info_mcp(query: str) -> str:
    """
    Fetch real-time web information on a given topic via Tavily.

    Use this before get_video_script_mcp to ground the script in
    current, accurate information from the web.

    Args:
        query: The topic or search query to research.

    Returns:
        Formatted string of search results — titles, URLs, and content snippets.

    Example:
        get_latest_info_mcp("AI agents trends 2025")
    """
    return get_realtime_info(query)


@mcp.tool()
def get_video_script_mcp(info_text: str) -> str:
    """
    Generate a structured YouTube video script from research content via Groq.

    Takes the research text from get_latest_info_mcp and produces a
    complete, production-ready YouTube script using LLaMA 3.3 70B on Groq.

    Script sections generated:
        - Hook
        - Introduction
        - Main content (research-backed sections)
        - Call to action
        - Outro

    Args:
        info_text: Research content from get_latest_info_mcp.

    Returns:
        A complete YouTube video script in markdown format.

    Example:
        info = get_latest_info_mcp("AI agents trends 2025")
        script = get_video_script_mcp(info)
    """
    return generate_video_script(info_text)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("YouTube Content Creation Agent — MCP Server")
    print("Tools:")
    print("  get_latest_info_mcp  — real-time research via Tavily")
    print("  get_video_script_mcp — script generation via Groq (LLaMA 3.3 70B)")
    print()
    mcp.run()