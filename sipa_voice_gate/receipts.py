"""Track 3 — verifiable receipts.

An append-only log where every entry is hash-chained to the one before it.
The claim is not "the agent says it did X" — it is a tamper-evident record of
what the gate decided and what actually ran, checkable by anyone with the file
and no trust in the agent.

Format: one JSON object per line (JSONL). Each entry:

    seq        running integer, starts at 0
    ts         unix time the entry was written
    kind       acted | acted_after_confirmation | blocked | confirm_requested | cancelled
    action     {type, description, args}
    decision   the gate decision as a dict
    note       free text (executor output, why cancelled, ...)
    prev_hash  hash of the previous entry (GENESIS for the first)
    hash       sha256(prev_hash + canonical(payload))
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

GENESIS = "0" * 64

# keys that go into the hash, in a fixed order
_PAYLOAD_KEYS = ("seq", "ts", "kind", "action", "decision", "note")


def _canonical(obj: Any) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def compute_hash(prev_hash: str, payload: dict) -> str:
    """sha256 over the previous hash plus the canonical form of this payload."""
    h = hashlib.sha256()
    h.update(prev_hash.encode("ascii"))
    h.update(_canonical({k: payload.get(k) for k in _PAYLOAD_KEYS}))
    return h.hexdigest()


@dataclass
class Receipt:
    seq: int
    ts: float
    kind: str
    action: dict
    decision: dict
    note: str
    prev_hash: str
    hash: str

    def to_dict(self) -> dict:
        return {
            "seq": self.seq,
            "ts": self.ts,
            "kind": self.kind,
            "action": self.action,
            "decision": self.decision,
            "note": self.note,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }


class ReceiptLog:
    """Open (or create) a log and append to it. Reopening continues the chain."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._last_hash = GENESIS
        self._seq = 0
        if self.path.exists():
            self._replay()

    def _replay(self) -> None:
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            self._last_hash = rec["hash"]
            self._seq = rec["seq"] + 1

    def append(self, kind: str, action: dict, decision: dict, note: str = "") -> Receipt:
        payload = {
            "seq": self._seq,
            "ts": time.time(),
            "kind": kind,
            "action": action,
            "decision": decision,
            "note": note,
        }
        entry_hash = compute_hash(self._last_hash, payload)
        r = Receipt(
            seq=payload["seq"],
            ts=payload["ts"],
            kind=kind,
            action=action,
            decision=decision,
            note=note,
            prev_hash=self._last_hash,
            hash=entry_hash,
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")
        self._last_hash = entry_hash
        self._seq += 1
        return r

    def entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def tape(self) -> list[dict]:
        """Trimmed view for the demo UI's receipt tape."""
        out = []
        for e in self.entries():
            out.append(
                {
                    "seq": e["seq"],
                    "ts": e["ts"],
                    "kind": e["kind"],
                    "what": e["action"]["description"],
                    "verdict": e["decision"].get("verdict"),
                    "hash": e["hash"][:12],
                }
            )
        return out
