"""Track 2 — the consequence gate.

Deterministic. Same answer at 3am and at noon. Fail-closed: an action that is
not provably safe does not get an ALLOW - it gets a CONFIRM (spoken out loud,
waits for an explicit yes) or a BLOCK.

Order of checks:
  1. hard invariants   -> BLOCK  (never allowed, not even with a yes)
  2. not consequential  -> ALLOW  (reversible, no external effect, no value moved)
  3. otherwise          -> CONFIRM (speak the consequence chain, wait for yes)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from .consequences import ConsequenceProfile, predict_consequences


class Verdict(str, Enum):
    ALLOW = "allow"
    CONFIRM = "confirm"
    BLOCK = "block"


@dataclass
class HardInvariant:
    name: str
    reason: str
    # (action_type, profile) -> True when the invariant is violated
    predicate: Callable[[str, ConsequenceProfile], bool]


DEFAULT_INVARIANTS: list[HardInvariant] = [
    HardInvariant(
        "value_ceiling",
        "the amount is over the ceiling this agent is trusted with",
        lambda t, p: p.moves_value and p.magnitude > 1000.0,
    ),
    HardInvariant(
        "irreversible_external_bulk",
        "an irreversible action hitting many external targets at once",
        lambda t, p: (not p.reversible) and p.external_effect and p.target_count > 25,
    ),
]


@dataclass
class GateDecision:
    verdict: Verdict
    reasons: list[str]
    consequence_chain: list[str]
    spoken: str

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict.value,
            "reasons": self.reasons,
            "consequence_chain": self.consequence_chain,
            "spoken": self.spoken,
        }


class ConsequenceGate:
    def __init__(self, invariants: list[HardInvariant] | None = None):
        self.invariants = list(DEFAULT_INVARIANTS if invariants is None else invariants)

    def evaluate(
        self, action_type: str, description: str, profile: ConsequenceProfile
    ) -> GateDecision:
        chain = predict_consequences(action_type, profile)

        violated = [inv for inv in self.invariants if inv.predicate(action_type, profile)]
        if violated:
            reasons = [f"{v.name}: {v.reason}" for v in violated]
            spoken = (
                f"I can't do that - {description}. "
                + " ".join(v.reason.capitalize() + "." for v in violated)
                + " You'll need to do this one yourself."
            )
            return GateDecision(Verdict.BLOCK, reasons, chain, spoken)

        if not profile.is_consequential():
            return GateDecision(
                Verdict.ALLOW,
                ["reversible, no external effect, no value moved"],
                chain,
                "",
            )

        reasons: list[str] = []
        if profile.moves_value:
            reasons.append("moves money")
        if profile.destroys_data:
            reasons.append("destroys data")
        if profile.changes_config:
            reasons.append("changes standing configuration")
        if profile.external_effect:
            reasons.append("has an effect outside this system")
        if not profile.reversible:
            reasons.append("cannot be undone")
        if not reasons:
            reasons.append("consequences are not fully known - asking to be safe")

        return GateDecision(Verdict.CONFIRM, reasons, chain, self._speak(description, chain))

    @staticmethod
    def _speak(description: str, chain: list[str]) -> str:
        d = description[:1].lower() + description[1:] if description else description
        parts = [f"You asked me to {d}."]
        if chain:
            parts.append("Here is what that does:")
            parts.append("; ".join(chain) + ".")
        parts.append("Say 'yes' to go ahead, or 'no' to stop.")
        return " ".join(parts)
