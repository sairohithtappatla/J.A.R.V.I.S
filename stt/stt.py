# 📁 stt.py — One-file Live STT with Whisper + VOSK fallback + multilingual support
import os
import time
import socket
import wave
import pyaudio
import numpy as np
import tempfile
import requests
import json
from vosk import Model, KaldiRecognizer


# 🌐 Internet check
def is_connected():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False


# 🧠 Whisper via Groq API (online STT)
def transcribe_with_whisper(audio_path, api_key):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}
    files = {
        "file": open(audio_path, "rb"),
        "model": (None, "whisper-large-v3"),
        "language": (None, "auto")
    }
    print("🌐 Transcribing using Whisper (Groq)...")
    response = requests.post(url, headers=headers, files=files)
    return response.json().get("text", "")


# 🧠 VOSK offline fallback
vosk_model = Model("vosk-model-small-multilingual")  # You can also use vosk-model-small-en-in, etc.

def transcribe_with_vosk(audio_path):
    wf = wave.open(audio_path, "rb")
    rec = KaldiRecognizer(vosk_model, wf.getframerate())
    result = ""
    print("📴 Transcribing using offline VOSK...")
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result += res.get("text", "") + " "
    return result.strip()


# 🎙️ Live mic recording with silence detection
def record_until_silence(threshold=500, silence_timeout=3, fs=16000):
    chunk = 1024
    format = pyaudio.paInt16
    channels = 1
    pa = pyaudio.PyAudio()
    stream = pa.open(format=format, channels=channels, rate=fs,
                     input=True, frames_per_buffer=chunk)

    print("🎙️ Live transcription started... Speak now")
    frames = []
    silent_chunks = 0
    speaking = False

    while True:
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

        audio_data = np.frombuffer(data, dtype=np.int16)
        energy = np.linalg.norm(audio_data)

        if energy > threshold:
            if not speaking:
                print("🎤 Detected speech...")
                speaking = True
            silent_chunks = 0
        else:
            if speaking:
                silent_chunks += 1
                if silent_chunks > (silence_timeout * fs / chunk):
                    print("🔇 Silence timeout reached.")
                    break

    stream.stop_stream()
    stream.close()
    pa.terminate()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wf = wave.open(f.name, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(pa.get_sample_size(format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        return f.name


# 🔁 Main transcriber function (auto Whisper or VOSK)
def start_live_transcription(groq_api_key):
    audio_file = record_until_silence()
    if is_connected():
        text = transcribe_with_whisper(audio_file, groq_api_key)
    else:
        text = transcribe_with_vosk(audio_file)

    print("\n📝 Transcription Result:", text)
    return text
