import os
from dotenv import load_dotenv
import assemblyai as aai
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY") or os.getenv("ASSEMBLYAI_KEY")

_elevenlabs_client = None


def _get_elevenlabs_client() -> ElevenLabs | None:
    global _elevenlabs_client
    if _elevenlabs_client is None:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            return None
        _elevenlabs_client = ElevenLabs(api_key=api_key)
    return _elevenlabs_client


# Redacts secret/credential-adjacent and personal-identifier categories from the
# transcript before it ever reaches the intent extractor / LLM. Substitution uses
# "entity_name" (e.g. "[PHONE_NUMBER]") rather than "hash" so the redaction is
# legible in the demo transcript panel, not just detectable.
_PII_POLICIES = [
    aai.PIIRedactionPolicy.password,
    aai.PIIRedactionPolicy.credit_card_number,
    aai.PIIRedactionPolicy.credit_card_cvv,
    aai.PIIRedactionPolicy.credit_card_expiration,
    aai.PIIRedactionPolicy.banking_information,
    aai.PIIRedactionPolicy.account_number,
    aai.PIIRedactionPolicy.us_social_security_number,
    aai.PIIRedactionPolicy.drivers_license,
    aai.PIIRedactionPolicy.passport_number,
    aai.PIIRedactionPolicy.email_address,
    aai.PIIRedactionPolicy.phone_number,
]

_TRANSCRIPTION_CONFIG = aai.TranscriptionConfig(
    redact_pii=True,
    redact_pii_policies=_PII_POLICIES,
    redact_pii_sub=aai.PIISubstitutionPolicy.entity_name,
)


def record_audio(duration: int = 5, sample_rate: int = 16000) -> bytes:
    import wave, io
    import pyaudio  # lazy: only needed for live mic capture, not for file-based/demo use
    CHUNK = 1024
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=sample_rate, input=True, frames_per_buffer=CHUNK)
    print(f"Recording for {duration}s...")
    frames = [stream.read(CHUNK) for _ in range(0, int(sample_rate / CHUNK * duration))]
    stream.stop_stream()
    stream.close()
    p.terminate()
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(p.get_sample_size(pyaudio.paFloat32))
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    return wav_buffer.getvalue()


def transcribe_with_pii_redaction(audio_bytes: bytes) -> str:
    result = aai.Transcriber(config=_TRANSCRIPTION_CONFIG).transcribe(audio_bytes)
    if result.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"AssemblyAI transcription failed: {result.error}")
    return result.text


def speak(text: str, voice_id: str = "GR6tdHEf644joXkoKyGi") -> None:
    """Speaks `text` aloud via ElevenLabs. Falls back to printing if no
    ELEVENLABS_API_KEY is configured, so the pipeline still runs without it."""
    client = _get_elevenlabs_client()
    if client is None:
        print(f"[TTS unavailable, no ELEVENLABS_API_KEY set — text was: {text}]")
        return
    audio = client.text_to_speech.convert(
        voice_id=voice_id,
        model_id="eleven_turbo_v2_5",
        text=text,
    )
    play(audio)


__all__ = ["record_audio", "transcribe_with_pii_redaction", "speak"]
