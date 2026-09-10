"""Track 3 — receipt verifier.

Recomputes the hash chain from scratch and reports any entry that was altered,
reordered, or dropped. Run it against a log you did not produce and it still
tells you whether the record is intact.

    python -m sipa_voice_gate.verifier receipts.log.jsonl
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .receipts import GENESIS, compute_hash, _PAYLOAD_KEYS


@dataclass
class VerifyResult:
    ok: bool
    count: int
    problems: list[str] = field(default_factory=list)


def verify(path: str | Path) -> VerifyResult:
    path = Path(path)
    if not path.exists():
        return VerifyResult(False, 0, [f"no such log: {path}"])

    problems: list[str] = []
    entries: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            problems.append(f"line {i}: not valid JSON ({exc})")

    prev = GENESIS
    for i, e in enumerate(entries):
        if e.get("seq") != i:
            problems.append(f"entry {i}: seq is {e.get('seq')}, expected {i} (entry dropped or reordered)")
        if e.get("prev_hash") != prev:
            problems.append(f"entry {i}: prev_hash does not match the previous entry's hash (chain broken)")
        payload = {k: e.get(k) for k in _PAYLOAD_KEYS}
        expected = compute_hash(e.get("prev_hash", ""), payload)
        if e.get("hash") != expected:
            problems.append(f"entry {i}: hash does not match its contents (entry was altered)")
        prev = e.get("hash", "")

    return VerifyResult(ok=not problems, count=len(entries), problems=problems)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: python -m sipa_voice_gate.verifier <log.jsonl>")
        return 2
    res = verify(argv[0])
    print(f"entries: {res.count}")
    if res.ok:
        print("OK - chain intact, nothing altered")
        return 0
    print("FAIL:")
    for p in res.problems:
        print(f"  - {p}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
