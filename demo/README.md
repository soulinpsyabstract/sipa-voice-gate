# Track 4 — Demo, UI & submission (the story)

Minimal web page: live transcript + gate decision + receipt tape, per docs/BUILD_PLAN.md.

## What's here

A small Flask app around the real `VoiceGateAgent` (tracks 2+3, untouched) — no mock data.
Every request goes through the actual consequence-gate and writes a real, hash-chained
receipt to `../receipts.jsonl`.

## Run it

```bash
pip install -r requirements.txt -r ../requirements.txt
python3 server.py
```

Open http://127.0.0.1:5050 — type an utterance (or click one of the examples) and watch
the gate decision + receipt tape update live. Try "Send $50 to Dana" (CONFIRM), then "yes"
(acts), then "Delete the backups folder" or "Send $5000 to Dana" (BLOCK — over the value
ceiling), then hit **Verify chain** to re-hash the whole log and confirm nothing was
altered.

The transcript field is typed text, standing in for what `../pipeline_agent.py` (Track 1)
already produces from a real mic through real AssemblyAI STT + PII redaction — that's a
separate terminal process, not duplicated here. This page's job is only the gate decision
and receipt tape, per the Track 4 deliverable.

## Still needed for submission (not code — see docs/BUILD_PLAN.md checklist)

- 2-minute demo video: one low-consequence request (acts fast), one high-consequence
  (stops, reads the consequence chain aloud via ElevenLabs, waits for "yes")
- lablab.ai project page filled in, team "sipaos" attached
- One-paragraph pitch text
- Submit by Sep 29 (one day of buffer before the Sep 30 deadline)
