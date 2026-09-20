"""Track 4 — demo web server.

Minimal Flask app around the real VoiceGateAgent (tracks 2+3, unmodified) —
no mock data, no simulated decisions. Every request goes through the actual
gate and the actual hash-chained receipt log.

    GET  /                render the demo page
    POST /api/hear         {"transcript": "..."} -> the agent's Turn as JSON
    GET  /api/tape         the receipt log, trimmed for display
    GET  /api/verify       re-hashes the whole chain, reports tamper status

The transcript here is typed, standing in for the post-STT-and-PII-redaction
text that `pipeline_agent.py` (Track 1) already produces from a real mic and
real AssemblyAI calls — that's a separate terminal process, not duplicated
here. This page's job is only the gate decision + receipt tape, per the
Track 4 deliverable in docs/BUILD_PLAN.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sipa_voice_gate.agent import VoiceGateAgent
from sipa_voice_gate.verifier import verify

RECEIPTS_PATH = Path(__file__).resolve().parent.parent / "receipts.jsonl"

app = Flask(__name__, static_folder="static", static_url_path="")
agent = VoiceGateAgent(log_path=RECEIPTS_PATH)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/hear")
def hear():
    body = request.get_json(force=True, silent=True) or {}
    transcript = (body.get("transcript") or "").strip()
    if not transcript:
        return jsonify({"error": "transcript is required"}), 400

    turn = agent.hear(transcript)
    return jsonify(
        {
            "transcript": turn.transcript,
            "intent": (
                {"type": turn.intent.action_type, "description": turn.intent.description}
                if turn.intent
                else None
            ),
            "verdict": turn.decision.verdict.value if turn.decision else None,
            "reasons": turn.decision.reasons if turn.decision else [],
            "consequence_chain": turn.decision.consequence_chain if turn.decision else [],
            "spoken": turn.spoken,
            "acted": turn.acted,
            "awaiting_confirmation": turn.awaiting_confirmation,
            "receipt_hash": turn.receipt_hash,
        }
    )


@app.get("/api/tape")
def tape():
    return jsonify(agent.log.tape())


@app.get("/api/verify")
def verify_chain():
    result = verify(RECEIPTS_PATH)
    return jsonify({"ok": result.ok, "count": result.count, "problems": result.problems})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
