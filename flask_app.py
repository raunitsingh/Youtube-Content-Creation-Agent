# Run locally:  python flask_app.py
# Run with gunicorn (production): gunicorn flask_app:app --bind 0.0.0.0:8080
#
# Endpoints:
#   GET  /health          — liveness check
#   POST /research        — run get_realtime_info()
#   POST /generate-script — run full pipeline (research + script)

import os

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import core functions — single source of truth shared with Streamlit UI
from app import get_realtime_info, generate_video_script


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Liveness check — used by Docker, Railway, and CI/CD pipelines."""
    return jsonify({"status": "ok", "service": "YouTube Content Creation Agent"}), 200


@app.post("/research")
def research():
    """
    Fetch real-time web research on a topic.

    Request body (JSON):
        { "query": "your topic here" }

    Response (JSON):
        { "query": "...", "info": "formatted research text" }
    """
    body = request.get_json(silent=True)

    if not body or not body.get("query", "").strip():
        return jsonify({"error": "Request body must include a non-empty 'query' field."}), 400

    query = body["query"].strip()

    try:
        info = get_realtime_info(query)
        return jsonify({"query": query, "info": info}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Research failed: {str(e)}"}), 500


@app.post("/generate-script")
def generate_script():
    """
    Run the full pipeline: research a topic then generate a YouTube script.

    Request body (JSON):
        { "topic": "your topic here" }

    Response (JSON):
        {
            "topic":  "...",
            "info":   "research text used",
            "script": "generated markdown script"
        }
    """
    body = request.get_json(silent=True)

    if not body or not body.get("topic", "").strip():
        return jsonify({"error": "Request body must include a non-empty 'topic' field."}), 400

    topic = body["topic"].strip()

    try:
        info   = get_realtime_info(topic)
        script = generate_video_script(info)
        return jsonify({"topic": topic, "info": info, "script": script}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Pipeline failed: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)