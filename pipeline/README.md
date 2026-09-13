# Track 1 — Voice Pipeline

**Mic → AssemblyAI STT → clean transcript → agent → speaker**

## What it does

- Records audio from mic
- Streams to AssemblyAI for real-time transcription
- Applies PII redaction (scaffolded, ready to enable)
- Passes clean transcript to VoiceGateAgent
- Speaks agent's response (TTS mocked due to ElevenLabs free tier)

## Quick start

```bash
python3 pipeline_agent.py
```

Record 5s of audio. Say something like "Send $50 to Dana" for a consequence gate test.

## Integration

```python
from pipeline import record_audio, transcribe_with_pii_redaction, speak
from sipa_voice_gate.agent import VoiceGateAgent

agent = VoiceGateAgent(log_path="receipts.jsonl")
audio = record_audio(duration=5)
transcript = transcribe_with_pii_redaction(audio)
turn = agent.hear(transcript)
speak(turn.spoken)
```

## Tests

All 21 core tests pass (sipa_voice_gate integrity preserved).

## Status

✅ STT (AssemblyAI)  
✅ Agent wiring  
✅ Test integration  
⚠️ TTS (ElevenLabs free account limitation)  
⚠️ PII redaction (scaffolded, needs AssemblyAI redaction policy config)
