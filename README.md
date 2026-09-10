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

| Dir | Track | Owner |
| --- | --- | --- |
| [`pipeline/`](pipeline/) | Voice pipeline — STT + PII redaction + TTS | — |
| [`agent-core/`](agent-core/) | Intent + consequence-gate + confirm-before-act loop | Aelin (gate design) |
| [`receipts/`](receipts/) | Append-only hashed action log + verifier | — |
| [`demo/`](demo/) | Web UI (transcript · gate decision · receipt tape) + submission | — |
| [`docs/`](docs/) | Build plan, timeline, checklist | — |

## Build plan

Full concept, work tracks, 20-day timeline, and submission checklist:
[docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)

## Team

Aelin AquaSoul · Benjamin · (+ up to 2) — team **sipaos** on lablab.ai

## License

Apache 2.0
