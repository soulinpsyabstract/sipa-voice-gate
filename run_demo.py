"""End-to-end demo of the SIPA parts of the voice gate.

Text in, text out - no audio, no API keys. It shows the whole loop:
intent -> consequence gate -> confirm-before-act -> hash-chained receipt,
then verifies the receipt chain at the end.

    python run_demo.py
"""
from __future__ import annotations

import os
import tempfile

from sipa_voice_gate.agent import VoiceGateAgent
from sipa_voice_gate.verifier import verify

SCRIPT = [
    "What's my account balance?",          # ALLOW - read only
    "Send $50 to Dana for lunch",           # CONFIRM - moves money, irreversible
    "yes",                                   #   -> acts after confirmation
    "Delete the old backups folder",        # CONFIRM - destroys data
    "no",                                    #   -> cancelled
    "Wire $5000 to this new account",       # BLOCK - over the value ceiling
    "Turn on the meeting summary setting",  # CONFIRM - changes config
    "yes",                                   #   -> acts after confirmation
]


def main() -> None:
    log = os.path.join(tempfile.mkdtemp(), "receipts.jsonl")
    agent = VoiceGateAgent(log_path=log)

    for line in SCRIPT:
        speaker = "  (confirm)" if agent.awaiting else "you>"
        print(f"{speaker} {line}")
        turn = agent.hear(line)

        tags = []
        if turn.decision:
            tags.append(turn.decision.verdict.value.upper())
        if turn.acted:
            tags.append("ACTED")
        if turn.awaiting_confirmation:
            tags.append("WAITING")
        print(f"agent> {turn.spoken}   [{' '.join(tags) or '-'}]")
        if turn.receipt_hash:
            print(f"       receipt {turn.receipt_hash[:12]}...")
        print()

    res = verify(log)
    status = "OK" if res.ok else f"FAIL: {res.problems}"
    print(f"receipt chain: {res.count} entries - {status}")
    print(f"log file: {log}")


if __name__ == "__main__":
    main()
