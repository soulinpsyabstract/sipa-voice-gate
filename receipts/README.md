# Track 3 — Receipts & audit (the proof)

**Status:** built, tested

Every path through the agent writes a receipt. The receipts are hash-chained:
each entry carries the hash of the one before it, so a single altered, dropped,
or reordered entry breaks verification. The claim is not "the agent says it did
X" — it is a tamper-evident record anyone can check with the file alone.

## Code

Lives in [`../sipa_voice_gate/`](../sipa_voice_gate):

| Module | What it does |
| --- | --- |
| `receipts.py` | `ReceiptLog` — append-only JSONL, `compute_hash`, `.tape()` view for the UI. |
| `verifier.py` | `verify(path)` + CLI. Recomputes the chain from scratch, lists every problem. |

## Entry shape (one JSON object per line)

```json
{"seq": 1, "ts": 1757500000.0, "kind": "acted_after_confirmation",
 "action": {"type": "send_money", "description": "send $50 to Dana", "args": {"amount": 50.0, "to": "dana"}},
 "decision": {"verdict": "confirm", "reasons": ["moves money", "cannot be undone"], "consequence_chain": ["..."], "spoken": "..."},
 "note": "[dry-run] transfer: {'amount': 50.0, 'to': 'dana'}",
 "prev_hash": "…", "hash": "…"}
```

`kind` ∈ `acted` · `acted_after_confirmation` · `blocked` · `confirm_requested` · `cancelled`

## Verify

```bash
python -m sipa_voice_gate.verifier receipts.jsonl
# entries: 8
# OK - chain intact, nothing altered
```

## Deliverable check

> log module + verifier + JSON for the UI

- log module — `ReceiptLog`
- verifier — `verify()` / `python -m sipa_voice_gate.verifier`
- JSON for the UI — `ReceiptLog(path).tape()` returns the trimmed list the demo's receipt tape renders
