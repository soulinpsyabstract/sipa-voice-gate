# Team status — sipa-voice-gate

**Date:** 2026-09-10 · **Submission deadline:** Sep 30 (lablab.ai, team `sipaos`)

## Where we are

The core is built, tested, and on `main` (commit `180e864`). This is the part
the whole demo depends on — intent → consequence gate → confirm-before-act →
verifiable receipt. Tracks 1 and 4 plug in on top of it and don't have to touch
this code.

```
you> What's my balance?              → acts immediately, writes a receipt
you> Send $50 to Dana                 → speaks the consequence chain, holds
  (confirm) yes                       → acts, writes a receipt
you> Wire $5000 to a new account      → BLOCK (over the trust ceiling)
you> Delete the backups
  (confirm) no                        → cancelled, nothing done
receipt chain: 8 entries — OK
```

Run it yourself: `pip install -e ".[dev]" && python run_demo.py` (no API keys).
Tests: `pytest -q` → 21 passing.

## What's done — `sipa_voice_gate/`

| Module | Purpose |
| --- | --- |
| `consequences.py` | Classifies an action (reversible? moves value? destroys data? external? config?) and predicts its downstream chain in plain language *before* it runs. |
| `gate.py` | `ConsequenceGate` — deterministic, fail-closed. Returns `ALLOW` / `CONFIRM` / `BLOCK` plus the exact text to speak. Hard invariants (never allowed): value over ceiling, irreversible action hitting >25 external targets. |
| `intent.py` | `IntentExtractor` interface + `KeywordIntentExtractor` fallback. **This is the seam Track 1 replaces.** |
| `actions.py` | Executor registry. Dry-run stubs today; `register("send_money", real_fn)` swaps in the real thing. |
| `agent.py` | `VoiceGateAgent.hear(transcript)` — the loop. Returns a `Turn` with `spoken`, `acted`, `awaiting_confirmation`, `receipt_hash`. |
| `receipts.py` | Append-only hash-chained JSONL log. `.tape()` gives the trimmed list for the UI. |
| `verifier.py` | `verify(path)` + `python -m sipa_voice_gate.verifier log.jsonl`. Recomputes the chain, catches any altered/dropped/reordered entry. |

## Open tasks by track

### Track 1 — Voice pipeline (STT + PII + TTS) — **needs an owner**
- AssemblyAI Universal-Streaming STT: mic audio → finalized transcript strings.
- AssemblyAI PII redaction on the transcript before it reaches intent extraction.
- Replace `KeywordIntentExtractor` with a LeMUR-backed one — same `extract(transcript) -> Intent | None` signature. `Intent` needs `action_type`, `description`, `args`, and a `ConsequenceProfile` (see `consequences.py` for the fields).
- ElevenLabs TTS: speak `turn.spoken` whenever it's non-empty.
- Wire it: on each finalized transcript call `agent.hear(text)`; if `turn.awaiting_confirmation`, the next transcript is the yes/no.

### Track 4 — Demo UI + submission — **needs an owner**
- Single web page, three panels: live transcript · current gate decision (verdict + reasons + consequence chain) · receipt tape (`ReceiptLog(path).tape()`).
- The gate decision panel is the whole story — show `BLOCK` and `CONFIRM` clearly.
- 2-minute demo video. Script it around the four cases in `run_demo.py`.
- lablab.ai project page + final README pass.

### Track 2 / 3 — mostly done, remaining polish
- Real executors for whatever the demo actually does (keep them dry-run for anything that moves real money).
- Tune `DEFAULT_INVARIANTS` if the demo needs different thresholds.
- Optional: a `/verify` button in the UI that runs `verify()` live on camera.

### Aelin
- Add Benjamin + teammates as GitHub collaborators (need your usernames — send them in the team chat).

## Design note — why it's built this way

We're not claiming a smarter model. The bet is a stricter loop around whatever
model does intent extraction: the gate is deterministic (same answer every
time), fails closed (anything not provably safe gets held or blocked, never
silently allowed), and every outcome leaves a receipt that someone else can
verify without trusting the agent. That's the SIPA OS thesis in voice form.
