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
# Core functions
# ---------------------------------------------------------------------------

def get_realtime_info(query: str) -> str:
    """
    Search the web for real-time information on the given topic using Tavily.

    Args:
        query: The YouTube topic to research.

    Returns:
        Formatted string of search results (titles, URLs, content snippets).
    """
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=6,
        include_answer=True,
    )

    lines = []

    # Top-level answer Tavily sometimes provides
    if response.get("answer"):
        lines.append(f"Summary: {response['answer']}\n")

    # Individual search results
    for i, result in enumerate(response.get("results", []), start=1):
        title   = result.get("title", "No title")
        url     = result.get("url", "")
        content = result.get("content", "").strip()

        lines.append(f"[{i}] {title}")
        lines.append(f"    Source: {url}")
        lines.append(f"    {content}")
        lines.append("")

    if not lines:
        raise ValueError(f"Tavily returned no results for query: '{query}'")

    return "\n".join(lines)


def generate_video_script(info_text: str) -> str:
    """
    Generate a structured YouTube video script from research text using Groq.

    Args:
        info_text: Research content returned by get_realtime_info().

    Returns:
        A complete, structured YouTube video script in markdown format.
    """
    prompt = f"""You are an expert YouTube scriptwriter. Using the research below, write a
complete, engaging YouTube video script. The script must follow this exact structure:

# [Video Title]

## Hook  (0-30 seconds)
An attention-grabbing opening statement or question. No fluff — pull the viewer in immediately.

## Introduction  (30-60 seconds)
Briefly introduce what the video covers and why the viewer should keep watching.

## Section 1: [Descriptive heading]
Talking points backed by the research. Write in a conversational, natural tone.

## Section 2: [Descriptive heading]
Continue with the next key idea from the research.

## Section 3: [Descriptive heading]
A third key idea or insight from the research.

## Call to Action
Ask the viewer to like, comment, and subscribe. Make it feel natural, not forced.

## Outro  (last 15 seconds)
A memorable closing line that wraps up the topic and teases future content.

---
Guidelines:
- Write in a conversational tone, as if speaking directly to the viewer.
- Each section should be 150-250 words of spoken script.
- Do not include stage directions or timestamps beyond the structure above.
- Do not fabricate statistics — use only what is in the research.
- The entire script should be 800-1200 words.

Research:
{info_text}

Write the full script now:"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional YouTube scriptwriter. "
                    "You write clear, engaging, research-backed video scripts. "
                    "Always follow the structure given by the user exactly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=2048,
    )

    script = response.choices[0].message.content

    if not script or not script.strip():
        raise ValueError("Groq returned an empty response. Try again.")

    return script.strip()


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
            except Exception as e:
                st.error(f"Research failed: {e}")
                info_text = None
                status.update(label="Research failed", state="error")

        # Step 2: Script generation
        if info_text:
            with st.status("Generating script with Groq...", expanded=True) as status:
                st.write(f"Model: {GROQ_MODEL}")
                try:
                    script = generate_video_script(info_text)
                    status.update(label="Script ready", state="complete")
                except Exception as e:
                    st.error(f"Script generation failed: {e}")
                    script = None
                    status.update(label="Generation failed", state="error")

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
        st.caption("Phase 2 — Core Development")


if __name__ == "__main__":
    main()