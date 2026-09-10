"""Track 2 - the confirm-before-act loop.

One method: `hear(transcript)`. It returns a `Turn` the voice pipeline turns
into speech. Every path writes a receipt.

    transcript -> intent -> gate
        BLOCK   -> speak refusal, write receipt, done
        ALLOW   -> act, write receipt, speak result
        CONFIRM -> speak the consequence chain, hold; next `hear()` must be
                   yes (act) or no (cancel); anything else keeps holding
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .actions import ActionOutcome, execute
from .gate import ConsequenceGate, GateDecision, Verdict
from .intent import Intent, IntentExtractor, KeywordIntentExtractor
from .receipts import ReceiptLog


@dataclass
class Turn:
    transcript: str
    intent: Intent | None
    decision: GateDecision | None
    spoken: str
    acted: bool
    outcome: ActionOutcome | None
    receipt_hash: str | None
    awaiting_confirmation: bool


_YES = {"yes", "yeah", "yep", "yup", "do it", "go ahead", "confirm", "proceed", "affirmative", "sure", "ok", "okay"}
_NO = {"no", "nope", "stop", "cancel", "abort", "negative", "don't", "do not"}


def _norm(t: str) -> str:
    return t.strip().lower().rstrip(".!?")


def _is_yes(t: str) -> bool:
    n = _norm(t)
    return n in _YES or n.startswith(("yes", "go ahead", "do it", "confirm", "proceed"))


def _is_no(t: str) -> bool:
    n = _norm(t)
    return n in _NO or n.startswith(("no", "stop", "cancel", "abort", "don't", "do not"))


def _action_dict(intent: Intent) -> dict:
    return {"type": intent.action_type, "description": intent.description, "args": intent.args}


class VoiceGateAgent:
    def __init__(
        self,
        log_path: str | Path = "receipts.log.jsonl",
        extractor: IntentExtractor | None = None,
        gate: ConsequenceGate | None = None,
    ):
        self.extractor = extractor or KeywordIntentExtractor()
        self.gate = gate or ConsequenceGate()
        self.log = ReceiptLog(log_path)
        self._pending: tuple[Intent, GateDecision] | None = None

    @property
    def awaiting(self) -> bool:
        return self._pending is not None

    def hear(self, transcript: str) -> Turn:
        if self._pending is not None:
            return self._resolve_pending(transcript)

        intent = self.extractor.extract(transcript)
        if intent is None:
            return Turn(
                transcript, None, None,
                "I didn't catch an action in that. Can you say it another way?",
                False, None, None, False,
            )

        decision = self.gate.evaluate(intent.action_type, intent.description, intent.profile)

        if decision.verdict is Verdict.BLOCK:
            r = self.log.append("blocked", _action_dict(intent), decision.as_dict())
            return Turn(transcript, intent, decision, decision.spoken, False, None, r.hash, False)

        if decision.verdict is Verdict.ALLOW:
            return self._act(transcript, intent, decision, confirmed=False)

        # CONFIRM
        self._pending = (intent, decision)
        self.log.append("confirm_requested", _action_dict(intent), decision.as_dict())
        return Turn(transcript, intent, decision, decision.spoken, False, None, None, True)

    def _resolve_pending(self, transcript: str) -> Turn:
        intent, decision = self._pending

        if _is_yes(transcript):
            self._pending = None
            return self._act(transcript, intent, decision, confirmed=True)

        if _is_no(transcript):
            self._pending = None
            r = self.log.append(
                "cancelled", _action_dict(intent), decision.as_dict(),
                note=f"user said: {transcript!r}",
            )
            return Turn(
                transcript, intent, decision,
                "Okay, cancelled. Nothing was done.",
                False, None, r.hash, False,
            )

        # neither yes nor no: stay closed, keep waiting
        return Turn(
            transcript, intent, decision,
            "I need a clear yes or no first. " + decision.spoken,
            False, None, None, True,
        )

    def _act(self, transcript: str, intent: Intent, decision: GateDecision, confirmed: bool) -> Turn:
        outcome = execute(intent.action_type, intent.args)
        kind = "acted_after_confirmation" if confirmed else "acted"
        r = self.log.append(kind, _action_dict(intent), decision.as_dict(), note=outcome.detail)
        spoken = ("Done. " + outcome.detail) if outcome.ok else ("That failed: " + outcome.detail)
        return Turn(transcript, intent, decision, spoken, outcome.ok, outcome, r.hash, False)
