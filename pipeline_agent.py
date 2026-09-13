#!/usr/bin/env python3
from pipeline import record_audio, transcribe_with_pii_redaction, speak
from sipa_voice_gate.agent import VoiceGateAgent

agent = VoiceGateAgent(log_path="receipts.jsonl")

print("Voice Gate Agent — Ready.\n")

while True:
    try:
        audio = record_audio(duration=5)
        transcript = transcribe_with_pii_redaction(audio)
        print(f"Transcript: {transcript}\n")
        
        turn = agent.hear(transcript)
        print(f"Agent: {turn.spoken}")
        speak(turn.spoken)
        print(f"Awaiting confirmation: {turn.awaiting_confirmation}\n")
        
    except KeyboardInterrupt:
        print("\nStopped.")
        break
    except Exception as e:
        print(f"Error: {e}\n")
        continue
