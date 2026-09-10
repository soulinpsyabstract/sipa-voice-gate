# Track 2 — Agent core & consequence-gate (brain & conscience)

**Owner:** Aelin (gate design) · **Status:** built, tested

Turn a transcript into a structured action, decide whether it is safe to run,
and either run it or speak the consequences and wait for an explicit yes.

## Code

Lives in [`../sipa_voice_gate/`](../sipa_voice_gate):

| Module | What it does |
| --- | --- |
| `intent.py` | `IntentExtractor` seam + `KeywordIntentExtractor` fallback. Real one plugs in AssemblyAI LeMUR / ask.sh. |
| `consequences.py` | `ConsequenceProfile` (the axes that matter) + `predict_consequences` (the downstream chain, worked out before the action runs). |
| `gate.py` | `ConsequenceGate` — deterministic, fail-closed. Returns `ALLOW` / `CONFIRM` / `BLOCK` + the spoken text. |
| `actions.py` | Executor registry. Dry-run stubs now; real integrations `register()` over them. |
| `agent.py` | `VoiceGateAgent.hear(transcript)` — the confirm-before-act loop. |

## Gate policy

1. **Hard invariants** → `BLOCK` (never allowed, not even with a yes). Default set: value over ceiling, irreversible action hitting >25 external targets. Extend `DEFAULT_INVARIANTS`.
2. **Not consequential** (reversible, no external effect, no value moved) → `ALLOW`.
3. **Everything else** → `CONFIRM`: speak the consequence chain, hold, require an explicit `yes`/`no`. Anything that isn't a clear yes/no keeps it held.

## Deliverable check

> given an intent, returns 'acted + receipt' or 'awaiting confirmation + spoken text'

```python
from sipa_voice_gate.agent import VoiceGateAgent
a = VoiceGateAgent(log_path="receipts.jsonl")

a.hear("What's my balance?")          # -> acted, receipt written
a.hear("Send $50 to Dana")            # -> awaiting confirmation + spoken text
a.hear("yes")                          # -> acted after confirmation, receipt written
```

See [`../run_demo.py`](../run_demo.py) for the full loop.

## Integration points for the team

- **Track 1** replaces `KeywordIntentExtractor` with a LeMUR-backed extractor (same `extract()` signature) and calls `agent.hear()` on each finished utterance; speaks `turn.spoken`.
- Real action executors: `from sipa_voice_gate.actions import register`.
