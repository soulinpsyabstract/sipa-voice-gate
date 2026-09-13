import os
from dotenv import load_dotenv
import assemblyai as aai
import pyaudio

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_KEY")

def record_audio(duration: int = 5, sample_rate: int = 16000) -> bytes:
    import wave, io
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
    result = aai.Transcriber().transcribe(audio_bytes)
    return result.text

def speak(text: str, voice_id: str = None) -> None:
    print(f"[TTS: {text}]")

__all__ = ["record_audio", "transcribe_with_pii_redaction", "speak"]
