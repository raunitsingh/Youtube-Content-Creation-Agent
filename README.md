A production-ready AI agent that researches any topic in real-time and generates a structured YouTube video script. Built with three consumption interfaces — a Streamlit web app, a Flask REST API, and an MCP server for direct AI agent integration.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [MCP Tools Reference](#mcp-tools-reference)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The **YouTube Content Creation Agent** is a multi-interface AI system built around two core functions:

1. **Research** — queries the Tavily Search API to pull real-time, accurate information on any topic from across the web
2. **Script generation** — feeds that research into **Groq (LLaMA 3.3 70B)** to produce a complete, production-ready YouTube video script

The same core logic is exposed through three interfaces simultaneously: a Streamlit web app for human users, a Flask REST API for programmatic access, and an MCP server so that any MCP-compatible AI agent can invoke the tools directly via tool calls — no duplication, one source of truth.

---

## Key Features

- **Real-time web research** — Tavily's advanced search mode pulls fresh, relevant content on any topic, not cached knowledge
- **Structured script generation** — LLaMA 3.3 70B on Groq produces a 7-section script (hook, intro, 3 content sections, CTA, outro) grounded in the research
- **Three interfaces, one codebase** — Streamlit UI, Flask REST API, and MCP server all import from the same `app.py` core functions
- **MCP-native** — exposes `get_latest_info_mcp` and `get_video_script_mcp` as discoverable tools for any AI agent with MCP client support
- **Containerised and CI/CD ready** — Dockerfile, Procfile, and a GitHub Actions pipeline that lints, builds, and smoke-tests on every push to `main`
- **Secure by default** — all credentials managed via `.env`, never hardcoded; non-root Docker user; XSRF protection enabled

---

## Architecture

### System diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                             CONSUMERS                                │
│                                                                      │
│   ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐  │
│   │   End User      │   │   REST Client    │   │   AI Agent      │  │
│   │   (Browser)     │   │   (curl / SDK)   │   │   (MCP Client)  │  │
│   └────────┬────────┘   └────────┬─────────┘   └────────┬────────┘  │
└────────────│────────────────────-│────────────────────── │───────────┘
             │                     │                        │
             ▼                     ▼                        ▼
   ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────┐
   │  Streamlit App   │  │  Flask REST API  │  │  MCP Server           │
   │  app.py          │  │  flask_app.py    │  │  mcp_server.py        │
   │  :8501           │  │  :8080           │  │  FastMCP              │
   └────────┬─────────┘  └────────┬─────────┘  └───────────┬───────────┘
            │                     │                          │
            └─────────────────────┴──────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     CORE LOGIC          │
                    │     app.py              │
                    │                         │
                    │  get_realtime_info()    │
                    │  generate_video_script()│
                    └────────────┬────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │                             │
                  ▼                             ▼
       ┌──────────────────┐         ┌──────────────────────┐
       │   Tavily API     │         │   Groq API           │
       │   Real-time      │         │   LLaMA 3.3 70B      │
       │   web search     │         │   Script generation  │
       └──────────────────┘         └──────────────────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                          ┌──────▼──────┐
                          │    .env     │
                          │  GROQ_KEY   │
                          │  TAVILY_KEY │
                          └─────────────┘
```

### Data flow

```
User Input (topic)
      │
      ▼
get_realtime_info(query)
      │
      ├──► Tavily Search API (search_depth="advanced", max_results=6)
      │         │
      │    Titles + URLs + content snippets
      │         │
      ◄─────────┘
      │
 Formatted research text
      │
      ▼
generate_video_script(info_text)
      │
      ├──► Groq — LLaMA 3.3 70B (temperature=0.7, max_tokens=2048)
      │         │
      │    Structured markdown script
      │         │
      ◄─────────┘
      │
      ▼
 Final script → Streamlit UI / Flask JSON response / MCP tool return
```

### Core functions

| Function | Input | Output | API |
|---|---|---|---|
| `get_realtime_info(query)` | Topic string | Numbered research blocks with titles, sources, and content | Tavily |
| `generate_video_script(info_text)` | Research text | 7-section YouTube script in markdown | Groq |

---

## Project Structure

```
youtube-content-creation-agent/
│
├── app.py                         # Core logic + Streamlit web UI
├── flask_app.py                   # Flask REST API (imports from app.py)
├── mcp_server.py                  # MCP server via FastMCP (imports from app.py)
│
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container definition for Flask API
├── Procfile                       # Railway / Heroku process declaration
│
├── .env                           # API keys — never commit this
├── .env.example                   # Safe template to commit
├── .gitignore
│
├── .streamlit/
│   └── config.toml                # Streamlit Cloud configuration + theme
│
└── .github/
    └── workflows/
        └── deploy.yml             # CI/CD: lint → build → health check
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web UI | Streamlit |
| REST API | Flask + Gunicorn |
| LLM / Script generation | Groq — LLaMA 3.3 70B Versatile |
| Real-time search | Tavily Search API |
| MCP server | FastMCP |
| Language | Python 3.11 |
| Containerisation | Docker |
| CI/CD | GitHub Actions |
| Config management | python-dotenv |
| Web deployment | Streamlit Community Cloud |
| API deployment | Railway / Heroku / Cloud Run |

---

## Prerequisites

- Python 3.10 or higher
- pip
- Docker (for containerised deployment only)
- A **Groq API key** — [console.groq.com/keys](https://console.groq.com/keys)
- A **Tavily API key** — [app.tavily.com/home](https://app.tavily.com/home)

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/youtube-content-creation-agent.git
cd youtube-content-creation-agent

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

```bash
# Copy the template
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

The app validates both keys on startup and exits with a clear error message if either is missing.

---

## Running the Application

### Streamlit web UI

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Enter a topic and click **Generate Script**. The UI shows live status for both the research and generation steps, then renders the script with a download button.

### Flask REST API

```bash
# Development
python flask_app.py

# Production
gunicorn flask_app:app --bind 0.0.0.0:8080 --workers 2 --timeout 120
```

Runs at `http://localhost:8080`. See [API Reference](#api-reference) for endpoints.

### MCP server

```bash
python mcp_server.py
```

Starts the FastMCP server and advertises two tools to any connected MCP client. See [MCP Tools Reference](#mcp-tools-reference).

---

## API Reference

### `GET /health`

Liveness check used by Docker, Railway, and the CI/CD pipeline.

**Response**

```json
{
  "status": "ok",
  "service": "YouTube Content Creation Agent"
}
```

---

### `POST /research`

Fetch real-time web research on a topic.

**Request body**

```json
{
  "query": "AI agents in 2027"
}
```

**Response**

```json
{
  "query": "AI agents in 2027",
  "info": "[1] Title of result\n    Source: https://...\n    Content snippet..."
}
```

---

### `POST /generate-script`

Run the full pipeline — research a topic and generate a complete YouTube script in a single call.

**Request body**

```json
{
  "topic": "AI agents in 2027"
}
```

**Response**

```json
{
  "topic": "AI agents in 2027",
  "info": "..research text used...",
  "script": "# Your Video Title\n\n## Hook\n..."
}
```

**Error responses** return a JSON object with an `"error"` key and an appropriate HTTP status code (400 for missing input, 404 if no results found, 500 for upstream failures).

---

## MCP Tools Reference

Both tools are registered on the FastMCP server and discoverable by any MCP-compatible AI agent.

### `get_latest_info_mcp`

Fetches real-time web information on a topic via Tavily.

| Parameter | Type | Description |
|---|---|---|
| `query` | `string` | The topic or search query |

Returns a formatted string of search results — titles, source URLs, and content snippets.

### `get_video_script_mcp`

Generates a structured YouTube script from research content via Groq.

| Parameter | Type | Description |
|---|---|---|
| `info_text` | `string` | Research content, typically from `get_latest_info_mcp` |

Returns a complete 7-section YouTube video script in markdown format.

**Typical agent workflow:**

```
info = get_latest_info_mcp("AI agents in 2027")
script = get_video_script_mcp(info)
```

---

## Deployment

### Streamlit Community Cloud

1. Push your repository to GitHub (ensure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select your repository and set the entry point to `app.py`
4. Under **Settings → Secrets**, add:

```toml
GROQ_API_KEY = "your_groq_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```

Streamlit Cloud reads `.streamlit/config.toml` automatically for theme and server settings.

---

### Docker

```bash
# Build the image
docker build -t youtube-agent .

# Run the container
docker run -p 8080:8080 --env-file .env youtube-agent
```

The container runs as a non-root user. Gunicorn is configured with 2 workers and a 120-second timeout to accommodate Groq response times.

---

### CI/CD via GitHub Actions

The pipeline at `.github/workflows/deploy.yml` runs automatically on every push to `main`:

| Job | What it does |
|---|---|
| **Lint** | Syntax-checks `app.py`, `flask_app.py`, and `mcp_server.py` via `py_compile` |
| **Build** | Builds the Docker image and pushes it to GitHub Container Registry (GHCR) |
| **Health check** | Spins up the container and hits `GET /health` — fails the pipeline if it does not return 200 |

Add these secrets to your GitHub repository under **Settings → Secrets → Actions**:

```
GROQ_API_KEY
TAVILY_API_KEY
GHCR_TOKEN    # GitHub personal access token with packages:write scope
```

---

### Railway / Heroku

Both platforms read the `Procfile` directly:

```
web: gunicorn flask_app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

Set `GROQ_API_KEY` and `TAVILY_API_KEY` as environment variables in the platform dashboard. No other configuration is needed.

---

## Environment Variables

| Variable | Required | Where to get it |
|---|---|---|
| `GROQ_API_KEY` | Yes | [console.groq.com/keys](https://console.groq.com/keys) |
| `TAVILY_API_KEY` | Yes | [app.tavily.com/home](https://app.tavily.com/home) |

---

## Contributing

```bash
# Fork the repo and create a branch
git checkout -b feature/your-feature

# Make your changes, then commit
git commit -m "Add your feature"

# Push and open a pull request
git push origin feature/your-feature
```

Please keep pull requests focused — one feature or fix per PR.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
