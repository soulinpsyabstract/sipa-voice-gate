"""Track 2 - intent extraction.

`IntentExtractor` is the seam. The real one uses AssemblyAI LeMUR (or an ask.sh
model) to turn a transcript into a structured action; `KeywordIntentExtractor`
is a dependency-free stand-in that is good enough to drive the gate and the demo.
Swap it at construction time:

    agent = VoiceGateAgent(extractor=LemurIntentExtractor(...))
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from .consequences import ConsequenceProfile

_MONEY = re.compile(r"(\d+(?:\.\d{1,2})?)")
_STOP = re.compile(r"[.,;!?]| and | please| now\b| for \b| tomorrow\b", re.IGNORECASE)


@dataclass
class Intent:
    action_type: str
    description: str          # verb phrase: "send $50 to Dana"
    args: dict = field(default_factory=dict)
    profile: ConsequenceProfile = field(default_factory=ConsequenceProfile)
    confidence: float = 1.0


class IntentExtractor(Protocol):
    def extract(self, transcript: str) -> Intent | None: ...


def _after(text: str, markers: tuple[str, ...]) -> str | None:
    for mk in markers:
        i = text.find(mk)
        if i != -1:
            tail = text[i + len(mk):].strip()
            tail = _STOP.split(tail)[0].strip()
            return tail or None
    return None


class KeywordIntentExtractor:
    """Rule-based fallback extractor. Order matters: most consequential first."""

    def extract(self, transcript: str) -> Intent | None:
        t = transcript.lower().strip()

        if any(w in t for w in ("send", "pay", "transfer", "wire")) and any(
            w in t for w in ("$", "dollar", "usd", "money", "payment")
        ):
            m = _MONEY.search(transcript)
            amount = float(m.group(1)) if m else 0.0
            who = _after(t, ("to ",)) or "the recipient"
            return Intent(
                "send_money",
                f"send ${amount:g} to {who}",
                {"amount": amount, "to": who},
                ConsequenceProfile(
                    reversible=False, external_effect=True, moves_value=True,
                    magnitude=amount, unit="USD",
                ),
            )

        if any(w in t for w in ("delete ", "remove ", "rm ", "wipe ")):
            target = _after(t, ("delete ", "remove ", "wipe ", "rm ")) or "the file"
            return Intent(
                "delete_file",
                f"delete {target}",
                {"target": target},
                ConsequenceProfile(reversible=False, destroys_data=True),
            )

        if "email" in t or ("send" in t and "message" in t) or "reply to" in t:
            who = _after(t, ("to ", "email ")) or "the recipient"
            return Intent(
                "send_email",
                f"email {who}",
                {"to": who},
                ConsequenceProfile(reversible=False, external_effect=True),
            )

        if any(w in t for w in ("buy ", "purchase ", "order ", "check out")):
            item = _after(t, ("buy ", "purchase ", "order ")) or "the item"
            return Intent(
                "purchase",
                f"buy {item}",
                {"item": item},
                ConsequenceProfile(reversible=False, external_effect=True, moves_value=True),
            )

        if any(w in t for w in ("set ", "change ", "enable ", "disable ", "turn off", "turn on")):
            return Intent(
                "change_setting",
                transcript.strip(),
                {"raw": transcript.strip()},
                ConsequenceProfile(reversible=True, changes_config=True),
            )

        if any(w in t for w in ("what", "show", "read", "check ", "how many", "list", "tell me", "when", "who")):
            return Intent(
                "read_data",
                transcript.strip(),
                {"query": transcript.strip()},
                ConsequenceProfile(reversible=True),
            )

        return None
