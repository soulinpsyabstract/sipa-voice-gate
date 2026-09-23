"""Demo-video script for the AssemblyAI Voice Agent Hackathon submission.

Real pipeline, paced for recording. Input audio is pre-generated (Aelin's own
ElevenLabs voice clone) instead of a live microphone — same real AssemblyAI
transcription + PII redaction, same real consequence-gate, same real
ElevenLabs TTS out. Only the mic-capture step is swapped for a file read.

    python demo_video_voice.py
"""
from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))

from pipeline import transcribe_with_pii_redaction, speak  # noqa: E402
from sipa_voice_gate.agent import VoiceGateAgent  # noqa: E402

PAUSE = 1.1
HERE = os.path.dirname(__file__)

TIMELINE_PATH = os.path.join(HERE, "demo_timeline.jsonl")
_T0 = time.time()
_LOG_LINES: list[str] = []


def _log_frame() -> None:
    with open(TIMELINE_PATH, "a") as f:
        f.write(json.dumps({"t": time.time() - _T0, "lines": list(_LOG_LINES)}) + "\n")


def beat(text: str = "", pause: float = PAUSE) -> None:
    print(text)
    sys.stdout.flush()
    _LOG_LINES.append(text)
    _log_frame()
    time.sleep(pause)


def run_turn(agent: VoiceGateAgent, label: str, audio_path: str) -> None:
    beat(f"\n>>> {label}")
    beat(f"    [voice in]  playing {os.path.basename(audio_path)} ...", pause=0.4)
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    beat("    [AssemblyAI] streaming transcription + PII redaction ...")
    transcript = transcribe_with_pii_redaction(audio_bytes)
    beat(f'    [transcript] "{transcript}"')

    turn = agent.hear(transcript)
    beat(f"    [gate]       verdict={turn.decision.verdict.value}  reasons={turn.decision.reasons}")
    if turn.decision.consequence_chain:
        beat("    [consequences]")
        for step in turn.decision.consequence_chain:
            beat(f"        - {step}")

    beat(f'    [agent says] "{turn.spoken}"')
    speak(turn.spoken)

    if turn.awaiting_confirmation:
        beat("    [state]      AWAITING CONFIRMATION — nothing happened yet.")
    elif turn.acted:
        beat(f"    [state]      ACTED. receipt={turn.receipt_hash[:12]}...")


def main() -> None:
    if os.path.exists(TIMELINE_PATH):
        os.remove(TIMELINE_PATH)
    log_path = os.path.join(HERE, "demo_receipts.jsonl")
    if os.path.exists(log_path):
        os.remove(log_path)
    agent = VoiceGateAgent(log_path=log_path)

    beat("=== sipa-voice-gate: the voice agent that checks itself before it acts ===")
    beat(">>> Team sipaos · AssemblyAI Voice Agent Hackathon\n")

    run_turn(agent, "TURN 1 — low consequence (should just act)",
              os.path.join(HERE, "..", "..", ".claude", "jobs", "b28c4699", "tmp", "voice_demo", "input_low.mp3"))

    run_turn(agent, "TURN 2 — high consequence (should stop and ask)",
              os.path.join(HERE, "..", "..", ".claude", "jobs", "b28c4699", "tmp", "voice_demo", "input_high.mp3"))

    beat("\n>>> Confirming the pending action by voice: \"yes\"")
    turn = agent.hear("yes")
    beat(f"    [gate]       verdict={turn.decision.verdict.value if turn.decision else 'n/a'}")
    beat(f'    [agent says] "{turn.spoken}"')
    speak(turn.spoken)
    if turn.acted:
        beat(f"    [state]      ACTED. receipt={turn.receipt_hash[:12]}...")

    beat("\n=== Not a bigger model — a stricter loop around it. ===", pause=0.3)


if __name__ == "__main__":
    main()
