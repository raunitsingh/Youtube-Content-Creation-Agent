# Run: streamlit run app.py

import os

from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient
import streamlit as st


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

GROQ_API_KEY  = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is missing. "
        "Copy .env.example to .env and add your key from https://console.groq.com/keys"
    )

if not TAVILY_API_KEY:
    raise EnvironmentError(
        "TAVILY_API_KEY is missing. "
        "Copy .env.example to .env and add your key from https://app.tavily.com/home"
    )

groq_client   = Groq(api_key=GROQ_API_KEY)
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

GROQ_MODEL = "llama-3.3-70b-versatile"


# ---------------------------------------------------------------------------
# Core functions  (Phase 2 implementation)
# ---------------------------------------------------------------------------

def get_realtime_info(query: str) -> str:
    """
    Search the web for real-time information on the given topic using Tavily.

    Args:
        query: The YouTube topic to research.

    Returns:
        Formatted string of search results (titles, URLs, content snippets).
    """
    raise NotImplementedError("get_realtime_info() will be implemented in Phase 2.")


def generate_video_script(info_text: str) -> str:
    """
    Generate a structured YouTube video script from research text using Groq.

    Args:
        info_text: Research content returned by get_realtime_info().

    Returns:
        A complete, structured YouTube video script in markdown format.
    """
    raise NotImplementedError("generate_video_script() will be implemented in Phase 2.")


# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(
        page_title="YouTube Content Creation Agent",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    st.title("YouTube Content Creation Agent")
    st.caption(
        "Enter a topic. The agent researches it in real-time and writes "
        "a production-ready video script."
    )
    st.divider()

    # Input
    topic = st.text_input(
        label="Video Topic",
        placeholder="e.g. The future of AI agents in 2025",
    )

    generate_btn = st.button(
        label="Generate Script",
        type="primary",
        use_container_width=True,
        disabled=not topic.strip(),
    )

    # Pipeline
    if generate_btn and topic.strip():

        # Step 1: Research
        with st.status("Researching topic...", expanded=True) as status:
            st.write("Querying Tavily for the latest information...")
            try:
                info_text = get_realtime_info(topic)
                st.write("Research complete.")
                status.update(label="Research done", state="complete")
            except NotImplementedError:
                st.warning("get_realtime_info() not yet implemented. Coming in Phase 2.")
                info_text = None
            except Exception as e:
                st.error(f"Research failed: {e}")
                info_text = None

        # Step 2: Script generation
        if info_text:
            with st.status("Generating script with Groq...", expanded=True) as status:
                st.write(f"Model: {GROQ_MODEL}")
                try:
                    script = generate_video_script(info_text)
                    status.update(label="Script ready", state="complete")
                except NotImplementedError:
                    st.warning("generate_video_script() not yet implemented. Coming in Phase 2.")
                    script = None
                except Exception as e:
                    st.error(f"Script generation failed: {e}")
                    script = None

            if script:
                st.divider()
                st.subheader("Your Video Script")
                st.markdown(script)

                st.download_button(
                    label="Download Script",
                    data=script,
                    file_name=f"{topic[:40].replace(' ', '_')}_script.md",
                    mime="text/markdown",
                )

    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        if GROQ_API_KEY:
            st.success("GROQ_API_KEY loaded")
        else:
            st.error("GROQ_API_KEY missing")

        if TAVILY_API_KEY:
            st.success("TAVILY_API_KEY loaded")
        else:
            st.error("TAVILY_API_KEY missing")

        st.caption(f"Model: {GROQ_MODEL}")
        st.divider()
        st.caption("Phase 1 — Infrastructure")


if __name__ == "__main__":
    main()