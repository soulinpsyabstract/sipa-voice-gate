# sipa-voice-gate

**The voice agent that checks itself before it acts.**

Built for the [AssemblyAI Voice Agent Hackathon](https://lablab.ai/ai-hackathons/assemblyai-voice-agent-hackathon)
(Sep 1–30, 2026) by team **sipaos**.

## The idea

A voice agent that listens with AssemblyAI, and **before it does anything with consequences** — send
money, delete a file, email someone, make a purchase — it speaks back a structured confirmation of
what it's about to do and the chain of consequences, and waits for an explicit spoken "yes." Every
action it takes is logged with a verifiable receipt.

Not a bigger model — a stricter loop around it.

## The flow

1. User speaks → **AssemblyAI Universal-Streaming STT** transcribes in real time
2. **AssemblyAI PII redaction** strips secrets/credentials from the transcript before it reaches the LLM
3. **Intent extraction** (AssemblyAI LeMUR, or an ask.sh model) → structured action
4. **Consequence-gate** classifies: reversible? moves money? deletes? sends externally?
5a. Low-consequence → agent acts, logs a receipt, confirms briefly by voice
5b. High-consequence → agent **speaks the consequence chain** (ElevenLabs), waits for explicit "yes", then acts
6. Every action → **verifiable receipt** (hashed, timestamped) in a live panel

## AssemblyAI features used

- Universal-Streaming STT (core — real-time transcription)
- PII redaction (transcript safety before LLM)
- LeMUR (intent extraction over the transcript)

## Repo structure

| Dir | Track | Owner | Status |
| --- | --- | --- | --- |
| [`sipa_voice_gate/`](sipa_voice_gate/) | The core package (tracks 2 + 3) | Aelin | **built, 21 tests** |
| [`pipeline/`](pipeline/) | Voice pipeline — STT + PII redaction + TTS | — | to build |
| [`agent-core/`](agent-core/) | Intent + consequence-gate + confirm-before-act loop | Aelin (gate design) | **built** → notes in dir |
| [`receipts/`](receipts/) | Append-only hashed action log + verifier | Aelin | **built** → notes in dir |
| [`demo/`](demo/) | Web UI (transcript · gate decision · receipt tape) + submission | — | to build |
| [`docs/`](docs/) | Build plan, timeline, checklist | — | — |

## Quickstart (the core, no API keys)

```bash
pip install -e ".[dev]"
python run_demo.py          # full loop: intent → gate → confirm → receipt → verify
pytest -q                   # 21 tests
python -m sipa_voice_gate.verifier receipts.jsonl
```

```python
from sipa_voice_gate.agent import VoiceGateAgent
agent = VoiceGateAgent(log_path="receipts.jsonl")
turn = agent.hear("Send $50 to Dana")   # -> turn.spoken is the consequence chain; agent.awaiting is True
turn = agent.hear("yes")                 # -> turn.acted is True; a receipt is written
```

## Build plan

Full concept, work tracks, 20-day timeline, and submission checklist:
[docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)

## Team

Aelin AquaSoul · Benjamin · (+ up to 2) — team **sipaos** on lablab.ai

## License

Apache 2.0
