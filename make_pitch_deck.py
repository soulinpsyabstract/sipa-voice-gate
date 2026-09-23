from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PAGE = landscape(letter)
W, H = PAGE

BG = HexColor("#0d1110")
FG = HexColor("#ece7de")
ACCENT = HexColor("#5fd6ae")
MUTED = HexColor("#96a099")

OUT = "/home/sipa/apps/sipa-voice-gate/pitch_deck.pdf"
c = canvas.Canvas(OUT, pagesize=PAGE)


def bg():
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def label(text, y=H - 0.9 * inch):
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(ACCENT)
    c.drawString(0.7 * inch, y, text.upper())


def title(text, y=H - 1.5 * inch, size=40):
    c.setFont("Helvetica-Bold", size)
    c.setFillColor(FG)
    c.drawString(0.7 * inch, y, text)


def body(lines, y_start, size=16, leading=24, color=FG):
    c.setFont("Helvetica", size)
    c.setFillColor(color)
    y = y_start
    for line in lines:
        c.drawString(0.7 * inch, y, line)
        y -= leading
    return y


def wrap(text, width=95):
    import textwrap
    return textwrap.wrap(text, width)


# Slide 1 — title
bg()
label("sipaos · AssemblyAI Voice Agent Hackathon")
title("sipa-voice-gate", y=H / 2 + 0.3 * inch, size=54)
c.setFont("Helvetica", 22)
c.setFillColor(MUTED)
c.drawString(0.7 * inch, H / 2 - 0.3 * inch, "The voice agent that checks itself before it acts.")
c.setFont("Helvetica", 14)
c.setFillColor(MUTED)
c.drawString(0.7 * inch, 0.7 * inch, "github.com/soulinpsyabstract/sipa-voice-gate")
c.showPage()

# Slide 2 — problem
bg()
label("Problem")
title("Voice agents that act blindly", size=34)
body(
    wrap(
        "Voice agents that can spend money, delete files, or send messages with "
        "no confirmation step are a live safety gap."
    ) + [""] + wrap(
        "Every other entry at this hackathon builds a faster, smoother voice "
        "assistant. None of them stop to check what they're about to do before "
        "doing it."
    ),
    y_start=H - 2.4 * inch,
)
c.showPage()

# Slide 3 — solution
bg()
label("Solution")
title("A stricter loop, not a bigger model", size=32)
body(
    wrap(
        "Before any action with real consequences — send money, delete a file, "
        "email someone, make a purchase — the agent speaks back a structured "
        "confirmation of what it's about to do and the chain of consequences, "
        "then waits for an explicit spoken \"yes.\""
    ) + [""] + wrap(
        "Every action, taken or blocked, is logged with a verifiable, "
        "hash-chained receipt."
    ),
    y_start=H - 2.4 * inch,
)
c.showPage()

# Slide 4 — how it works
bg()
label("How it works")
title("Six steps", size=34)
steps = [
    "1. AssemblyAI Universal-Streaming STT transcribes in real time",
    "2. AssemblyAI PII redaction strips secrets before the LLM sees them",
    "3. AssemblyAI LeMUR extracts a structured action from the transcript",
    "4. Consequence-gate classifies it: reversible? moves money? deletes?",
    "5. Low consequence -> acts + logs a receipt. High -> speaks the",
    "   consequence chain and waits for an explicit \"yes\"",
    "6. Every action writes a hash-chained receipt; a verifier catches tampering",
]
body(steps, y_start=H - 2.2 * inch, size=15, leading=26)
c.showPage()

# Slide 5 — stack
bg()
label("Tech stack")
title("Real AssemblyAI, real gate, real receipts", size=26)
body(
    [
        "AssemblyAI: Universal-Streaming STT, PII redaction, LeMUR",
        "ElevenLabs: TTS for the agent's spoken confirmations",
        "Python: consequence-gate, hash-chained receipt log, verifier",
        "21 tests green, runs the full loop with zero API keys (run_demo.py)",
    ],
    y_start=H - 2.2 * inch,
    size=17,
    leading=30,
)
c.showPage()

# Slide 6 — team
bg()
label("Team — sipaos")
title("Three people, three tracks", size=32)
body(
    [
        "Aelin AquaSoul — consequence-gate design, core package, receipts",
        "   + verifier, real PII redaction + ElevenLabs TTS wiring, demo UI",
        "Gephel — voice pipeline (AssemblyAI STT integration, agent wiring)",
        "Benjamin Hong — security review of the consequence-gate,",
        "   adversarial test suite",
    ],
    y_start=H - 2.2 * inch,
    size=16,
    leading=28,
)
c.showPage()

# Slide 7 — closing
bg()
c.setFont("Helvetica-BoldOblique", 30)
c.setFillColor(ACCENT)
c.drawCentredString(W / 2, H / 2, "Not a bigger model —")
c.drawCentredString(W / 2, H / 2 - 0.6 * inch, "a stricter loop around it.")
c.showPage()

c.save()
print("saved", OUT)
