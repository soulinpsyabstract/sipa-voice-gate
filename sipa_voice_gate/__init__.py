"""SIPA parts of the self-checking voice agent.

Track 2 (agent-core): consequence gate + confirm-before-act loop.
Track 3 (receipts):   append-only hash-chained action log + verifier.

Nothing here needs an API key or audio. The voice pipeline (Track 1) and the
demo UI (Track 4) sit on top of this core.
"""
from .consequences import ConsequenceProfile, predict_consequences
from .gate import ConsequenceGate, GateDecision, Verdict, HardInvariant
from .intent import Intent, IntentExtractor, KeywordIntentExtractor
from .agent import VoiceGateAgent, Turn
from .receipts import ReceiptLog, Receipt, compute_hash, GENESIS
from .verifier import verify, VerifyResult

__all__ = [
    "ConsequenceProfile",
    "predict_consequences",
    "ConsequenceGate",
    "GateDecision",
    "Verdict",
    "HardInvariant",
    "Intent",
    "IntentExtractor",
    "KeywordIntentExtractor",
    "VoiceGateAgent",
    "Turn",
    "ReceiptLog",
    "Receipt",
    "compute_hash",
    "GENESIS",
    "verify",
    "VerifyResult",
]
