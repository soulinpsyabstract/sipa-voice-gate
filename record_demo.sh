#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export ASSEMBLYAI_API_KEY="$(grep '^ASSEMBLYAI_API_KEY=' ~/.sipa_env | tail -1 | cut -d= -f2- | tr -d '"')"
export ELEVENLABS_API_KEY="$(grep '^ELEVENLABS_API_KEY=' ~/.sipa_env | tail -1 | cut -d= -f2- | tr -d '"')"

rm -f demo_audio.wav demo_timeline.jsonl demo_receipts.jsonl

# Start capturing the system audio output (what speak()/play() sends to the
# null sink) in the background, then run the demo, then stop the capture.
ffmpeg -y -f pulse -i auto_null.monitor demo_audio.wav > ffmpeg_audio.log 2>&1 &
FFMPEG_PID=$!
sleep 1

python3 demo_video_voice.py

sleep 1
kill -INT "$FFMPEG_PID" 2>/dev/null || true
wait "$FFMPEG_PID" 2>/dev/null || true

echo "--- audio captured ---"
ls -la demo_audio.wav

python3 render_frames.py
