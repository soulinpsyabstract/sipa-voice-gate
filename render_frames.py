"""Render demo_timeline.jsonl into numbered terminal-style PNG frames, then
concat them into a silent video and mux the recorded audio track on top.

    python render_frames.py
"""
from __future__ import annotations

import json
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(__file__)
TIMELINE_PATH = os.path.join(HERE, "demo_timeline.jsonl")
FRAMES_DIR = os.path.join(HERE, "demo_frames")
AUDIO_PATH = os.path.join(HERE, "demo_audio.wav")
OUT_VIDEO_NOAUDIO = os.path.join(HERE, "demo_video_noaudio.mp4")
OUT_FINAL = os.path.join(HERE, "demo_final.mp4")

W, H = 1280, 720
BG = (13, 17, 15)
FG = (210, 235, 220)
ACCENT = (95, 214, 174)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SIZE = 22
LINE_H = 30
MARGIN = 36

font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
title_font = ImageFont.truetype(FONT_PATH, 26)


def render_frame(lines: list[str], path: str) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((MARGIN, 16), "sipa-voice-gate — live demo", font=title_font, fill=ACCENT)
    d.line([(MARGIN, 54), (W - MARGIN, 54)], fill=(40, 48, 44), width=1)

    visible = lines[-20:]
    y = 70
    for line in visible:
        color = ACCENT if line.strip().startswith(">>>") else FG
        # wrap long lines
        max_chars = 118
        wrapped = [line[i:i + max_chars] for i in range(0, max(len(line), 1), max_chars)] or [""]
        for w_line in wrapped:
            d.text((MARGIN, y), w_line, font=font, fill=color)
            y += LINE_H
    img.save(path)


def main() -> None:
    os.makedirs(FRAMES_DIR, exist_ok=True)
    for f in os.listdir(FRAMES_DIR):
        os.remove(os.path.join(FRAMES_DIR, f))

    entries = []
    with open(TIMELINE_PATH) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    if not entries:
        raise SystemExit("demo_timeline.jsonl is empty — run demo_video_voice.py first")

    # duration of each frame = gap to next entry; last frame gets a 3s tail
    concat_list_path = os.path.join(FRAMES_DIR, "concat.txt")
    with open(concat_list_path, "w") as concat_f:
        for i, entry in enumerate(entries):
            frame_path = os.path.join(FRAMES_DIR, f"frame_{i:04d}.png")
            render_frame(entry["lines"], frame_path)
            if i + 1 < len(entries):
                dur = max(entries[i + 1]["t"] - entry["t"], 0.05)
            else:
                dur = 3.0
            concat_f.write(f"file 'frame_{i:04d}.png'\nduration {dur:.3f}\n")
        # ffmpeg concat demuxer quirk: repeat last file once more without duration
        concat_f.write(f"file 'frame_{len(entries)-1:04d}.png'\n")

    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
            "-vsync", "vfr", "-pix_fmt", "yuv420p", OUT_VIDEO_NOAUDIO,
        ],
        cwd=FRAMES_DIR,
        check=True,
    )

    if os.path.exists(AUDIO_PATH):
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", OUT_VIDEO_NOAUDIO, "-i", AUDIO_PATH,
                "-c:v", "copy", "-c:a", "aac", "-shortest", OUT_FINAL,
            ],
            check=True,
        )
        print(f"Final video with audio: {OUT_FINAL}")
    else:
        print(f"No audio track found at {AUDIO_PATH} — silent video only: {OUT_VIDEO_NOAUDIO}")


if __name__ == "__main__":
    main()
