# Architecture:
#   User (browser) → Streamlit UI → get_realtime_info() → Tavily API
#                                 → generate_video_script() → Gemini API

import os 
from dotenv import load_dotenv
import google.generativeai as genai
from tavily import TavilyClient
import streamlit as st

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate that both keys are present before the app starts
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY is missing. "
        "Copy .env.example → .env and add your key."
    )

if not TAVILY_API_KEY:
    raise EnvironmentError(
        "TAVILY_API_KEY is missing. "
        "Copy .env.example → .env and add your key."
    )


# ── 2. Initialise API clients ─────────────────────────────────────────────────
# Configure the Gemini SDK with the API key
genai.configure(api_key=GEMINI_API_KEY)

# Initialise the Tavily search client
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Gemini model to use for script generation
GEMINI_MODEL = "gemini-2.0-flash"


# ── 3. Core functions (stubs — implemented in Phase 2) ───────────────────────

def get_realtime_info(query: str) -> str:
    """
    Fetch real-time web information for the given topic using Tavily.

    Args:
        query (str): The YouTube topic to research.

    Returns:
        str: Formatted string of recent search results.

    Phase 2 TODO:
        - Call tavily_client.search(query, ...)
        - Extract and format result titles, URLs, and content snippets
        - Return as a clean text block for Gemini to consume
    """
    # ── Phase 2 implementation goes here ──────────────────────────────────────
    raise NotImplementedError("get_realtime_info() will be implemented in Phase 2.")


def generate_video_script(info_text: str) -> str:
    """
    Generate a structured YouTube video script from research content using Gemini.

    Args:
        info_text (str): The research text returned by get_realtime_info().

    Returns:
        str: A complete, structured YouTube video script.

    Phase 2 TODO:
        - Build a prompt that instructs Gemini to write a YouTube script
        - Include sections: Hook, Introduction, Main Content, CTA, Outro
        - Call genai.GenerativeModel(GEMINI_MODEL).generate_content(prompt)
        - Return the generated text
    """
    # ── Phase 2 implementation goes here ──────────────────────────────────────
    raise NotImplementedError("generate_video_script() will be implemented in Phase 2.")


# ── 4. Streamlit UI ───────────────────────────────────────────────────────────

def main():
    """Entry point for the Streamlit web application."""

    # Page configuration
    st.set_page_config(
        page_title="YouTube Content Creation Agent",
        page_icon="🎬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # ── Header ────────────────────────────────────────────────────────────────
    st.title("🎬 YouTube Content Creation Agent")
    st.markdown(
        "Enter a topic below. The agent will **research it in real-time** "
        "and generate a **production-ready video script** for you."
    )
    st.divider()

    # ── Input ─────────────────────────────────────────────────────────────────
    topic = st.text_input(
        label="Video Topic",
        placeholder="e.g. The future of AI agents in 2025",
        help="Enter the subject you want to create a YouTube video about.",
    )

    generate_btn = st.button(
        label="🚀 Generate Script",
        type="primary",
        use_container_width=True,
        disabled=not topic.strip(),
    )

    # ── Generation pipeline ───────────────────────────────────────────────────
    if generate_btn and topic.strip():

        # Step 1: Real-time research
        with st.status("🔍 Researching your topic in real-time...", expanded=True) as status:
            st.write("Querying Tavily for the latest information...")
            try:
                info_text = get_realtime_info(topic)
                st.write("✅ Research complete.")
            except NotImplementedError:
                st.warning("⚠️ get_realtime_info() not yet implemented — coming in Phase 2.")
                info_text = None
            except Exception as e:
                st.error(f"Research failed: {e}")
                info_text = None

        # Step 2: Script generation
        if info_text:
            with st.status("✍️ Generating your video script with Gemini...", expanded=True) as status:
                st.write(f"Using model: `{GEMINI_MODEL}`")
                try:
                    script = generate_video_script(info_text)
                    status.update(label="✅ Script ready!", state="complete")
                except NotImplementedError:
                    st.warning("⚠️ generate_video_script() not yet implemented — coming in Phase 2.")
                    script = None
                except Exception as e:
                    st.error(f"Script generation failed: {e}")
                    script = None

            # ── Output ────────────────────────────────────────────────────────
            if script:
                st.divider()
                st.subheader("📄 Your Video Script")
                st.markdown(script)

                # Download button
                st.download_button(
                    label="⬇️ Download Script",
                    data=script,
                    file_name=f"{topic[:40].replace(' ', '_')}_script.md",
                    mime="text/markdown",
                )

    # ── Sidebar: API status ───────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.success("✅ GEMINI_API_KEY loaded") if GEMINI_API_KEY else st.error("❌ GEMINI_API_KEY missing")
        st.success("✅ TAVILY_API_KEY loaded") if TAVILY_API_KEY else st.error("❌ TAVILY_API_KEY missing")
        st.caption(f"Model: `{GEMINI_MODEL}`")
        st.divider()
        st.caption("YouTube Content Creation Agent · Phase 1")


# ── 5. Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()