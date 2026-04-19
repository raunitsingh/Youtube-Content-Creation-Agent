# YouTube Content Creation Agent

> An AI-powered agent that researches any topic in real-time and generates a production-ready YouTube video script — exposed both as a web app and as an MCP server for AI agent integration.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
  - [System Components](#system-components)
  - [Data Flow](#data-flow)
  - [Core Functions](#core-functions)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
  - [Streamlit Web UI](#streamlit-web-ui)
  - [MCP Server](#mcp-server)
- [MCP Tools Reference](#mcp-tools-reference)
- [Build Phases](#build-phases)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **YouTube Content Creation Agent** is a multi-interface AI system that takes a user-provided topic, fetches live information from the web using **Tavily**, and generates a structured, high-quality video script using **Google Gemini (gemini-2.0-flash)**.

It is built with two consumption surfaces:

1. **Streamlit Web App** — a browser-based UI for human users
2. **MCP Server (FastMCP)** — a programmatic interface for AI agents via the Model Context Protocol

---

## Key Features

- **Real-time research** — uses Tavily Search API to pull fresh, up-to-date content on any topic
- **AI script generation** — Gemini summarises research and produces a structured YouTube script with intro, body, and outro
- **Dual interface** — same core logic powers both the web UI and the MCP server
- **MCP integration** — any MCP-compatible AI agent (e.g. Claude) can call the agent's tools programmatically via tool calls
- **Environment-based config** — all API keys stored securely in `.env`

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONSUMERS                                │
│                                                                 │
│   ┌─────────────────┐              ┌─────────────────────────┐  │
│   │   End User      │              │    AI Agents            │  │
│   │   (Browser)     │              │    (MCP Clients)        │  │
│   └────────┬────────┘              └────────────┬────────────┘  │
│            │ Topic query                        │ Tool calls    │
└────────────│────────────────────────────────────│───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────┐              ┌─────────────────────────────┐
│  Streamlit App     │              │  MCP Server (mcp_server.py) │
│  (app.py · Web UI) │──────────►  │  FastMCP framework          │
│                    │   Core Logic │  Tools: get_latest_info_mcp │
└────────────────────┘              │          get_video_script_mcp│
             │                      └─────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                     CORE LOGIC  (app.py)                       │
│                                                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  get_realtime_info(query)                               │  │
│   │  → calls Tavily → returns raw search results as text   │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  generate_video_script(info_text)                       │  │
│   │  → sends results to Gemini → returns structured script  │  │
│   └─────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────┬──────────────────┘
                           │                  │
              Search ▼     │                  │  ▲ Script
                           ▼                  ▼
              ┌────────────────┐    ┌────────────────────────┐
              │  Tavily API    │    │   Google Gemini         │
              │  Real-time     │    │   gemini-2.0-flash      │
              │  Web Search    │    │   Summarise & Generate  │
              └────────────────┘    └────────────────────────┘
                           │                  │
                           └──────┬───────────┘
                                  │
                            ┌─────▼──────┐
                            │   .env     │
                            │ GEMINI_KEY │
                            │ TAVILY_KEY │
                            └────────────┘
```

### Data Flow

```
User Input (Topic)
       │
       ▼
get_realtime_info(query)
       │
       ├──► Tavily Search API
       │         │
       │    Search Results (JSON)
       │         │
       ◄─────────┘
       │
  info_text (formatted string)
       │
       ▼
generate_video_script(info_text)
       │
       ├──► Google Gemini (gemini-2.0-flash)
       │         │
       │    Generated Script (markdown)
       │         │
       ◄─────────┘
       │
       ▼
  Final Script → displayed in Streamlit UI / returned via MCP tool
```

### Core Functions

| Function | Input | Output | External Call |
|---|---|---|---|
| `get_realtime_info(query)` | Topic string | Formatted research text | Tavily Search API |
| `generate_video_script(info_text)` | Research text | Structured video script | Google Gemini API |

---

## Project Structure

```
youtube-content-creation-agent/
│
├── app.py                  # Core logic + Streamlit web UI
├── mcp_server.py           # MCP server exposing tools via FastMCP
├── .env                    # API keys (never commit this)
├── .env.example            # Template for environment variables
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
└── (optional)
    ├── utils/              # Shared helper functions
    └── tests/              # Unit and integration tests
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web UI | Streamlit |
| AI / Script Generation | Google Gemini — `gemini-2.0-flash` |
| Real-time Search | Tavily Search API |
| MCP Server Framework | FastMCP |
| Language | Python 3.10+ |
| Config Management | python-dotenv |
| Deployment (Web) | Streamlit Community Cloud |
| Deployment (API) | Flask + CI/CD pipeline |

---

## Prerequisites

Before you begin, ensure you have the following:

- Python 3.10 or higher
- `pip` package manager
- A **Tavily API key** — sign up at [tavily.com](https://tavily.com)
- A **Google Gemini API key** — get one from [Google AI Studio](https://aistudio.google.com)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/youtube-content-creation-agent.git
cd youtube-content-creation-agent
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configuration

### 1. Create your `.env` file

```bash
cp .env.example .env
```

### 2. Fill in your API keys

```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> **Security note:** Never commit your `.env` file to version control. It is already listed in `.gitignore`.

---

## Running the App

### Streamlit Web UI

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`. Enter a topic and click **Generate Script** to get your research-backed video script.

### MCP Server

```bash
python mcp_server.py
```

This starts the FastMCP server and exposes the tools over the Model Context Protocol. AI agents with MCP client support can now call `get_latest_info_mcp` and `get_video_script_mcp` as tool calls.

---

## MCP Tools Reference

### `get_latest_info_mcp`

Fetches real-time web information on a given topic using Tavily.

| Parameter | Type | Description |
|---|---|---|
| `query` | `string` | The topic or search query |

**Returns:** A formatted string of recent search results relevant to the topic.

---

### `get_video_script_mcp`

Generates a structured YouTube video script from research text using Gemini.

| Parameter | Type | Description |
|---|---|---|
| `info_text` | `string` | Research content (typically the output of `get_latest_info_mcp`) |

**Returns:** A structured video script with hook, introduction, main sections, call to action, and outro.

---

## Build Phases

This project was built phase by phase following a structured curriculum:

### Phase 1 — Preparation & Infrastructure
- Project introduction and architecture walkthrough
- Repository setup and folder structure
- Virtual environment and `requirements.txt`
- API key acquisition (Tavily + Gemini)

### Phase 2 — Core Development
- `get_realtime_info()` function using Tavily
- `generate_video_script()` function using Gemini
- `mcp_server.py` — wrapping both functions as MCP tools via FastMCP

### Phase 3 — Completion
- Streamlit UI integration
- End-to-end testing with real topics
- Final demo

### Phase 4 — Deployment
- Streamlit Community Cloud deployment
- Flask app packaging for CI/CD
- Production-ready configuration

---

## Deployment

### Streamlit Community Cloud

1. Push your code to a public GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository and set `app.py` as the entry point
4. Add your environment variables (`GEMINI_API_KEY`, `TAVILY_API_KEY`) in the secrets manager

### Flask + CI/CD

For production API deployment, the project can be wrapped in a Flask app and deployed via a CI/CD pipeline (e.g. GitHub Actions → Cloud Run / Heroku / Railway).

```bash
# Example: running as Flask app
flask run --host=0.0.0.0 --port=8080
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes | Google Gemini API key from AI Studio |
| `TAVILY_API_KEY` | Yes | Tavily Search API key |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

*Built with Streamlit · Google Gemini · Tavily · FastMCP*