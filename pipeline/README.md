# Track 1 — Voice Pipeline

**Mic → AssemblyAI STT → clean transcript → agent → speaker**

## What it does

- Records audio from mic
- Streams to AssemblyAI for real-time transcription
- Applies PII redaction (password, card/banking, SSN, driver's license, passport,
  email, phone — substituted as readable `[ENTITY_NAME]` tags, not just hashed)
- Passes clean transcript to VoiceGateAgent
- Speaks agent's response via ElevenLabs (falls back to printing the text if
  `ELEVENLABS_API_KEY` isn't set, so the pipeline still runs without it)

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
✅ TTS (ElevenLabs, real audio — verified with a live API call, not just wired)  
✅ PII redaction (real AssemblyAI redaction policy config, verified end-to-end:
   a test phrase with a phone number and email transcribed to `[PHONE_NUMBER]`
   and `[EMAIL_ADDRESS]`, confirming redaction happens before the transcript
   ever reaches the intent extractor)

## Setup

```bash
pip install -r ../requirements.txt
cp ../.env.example ../.env   # then fill in ASSEMBLYAI_KEY and ELEVENLABS_API_KEY
```

`pyaudio` needs PortAudio installed on the system first (`apt install
portaudio19-dev` on Debian/Ubuntu, `brew install portaudio` on macOS) — its
Python wheel won't build without it.
