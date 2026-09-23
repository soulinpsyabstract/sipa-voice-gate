from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (13, 17, 15)
FG = (236, 231, 222)
ACCENT = (95, 214, 174)
MUTED = (150, 160, 155)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 92)
tagline_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
label_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 28)
small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 26)

d.text((100, 90), "sipaos · AssemblyAI Voice Agent Hackathon", font=label_font, fill=ACCENT)
d.line([(100, 140), (W - 100, 140)], fill=(40, 48, 44), width=2)

d.text((100, 420), "sipa-voice-gate", font=title_font, fill=FG)
d.text((100, 540), "The voice agent that checks itself before it acts.", font=tagline_font, fill=MUTED)

# three small chips
chips = ["AssemblyAI STT + PII", "Consequence-gate", "Verifiable receipts"]
x = 100
y = 640
for chip in chips:
    bbox = d.textbbox((0, 0), chip, font=small_font)
    w = bbox[2] - bbox[0] + 40
    d.rounded_rectangle([x, y, x + w, y + 56], radius=28, outline=ACCENT, width=2)
    d.text((x + 20, y + 14), chip, font=small_font, fill=ACCENT)
    x += w + 20

d.text((100, H - 120), "github.com/soulinpsyabstract/sipa-voice-gate", font=small_font, fill=MUTED)

img.save("/home/sipa/apps/sipa-voice-gate/cover_image.png")
print("saved cover_image.png")
