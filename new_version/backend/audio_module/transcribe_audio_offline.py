import os
import queue
import sounddevice as sd
import vosk
import json
import numpy as np
import soundfile as sf
from datetime import datetime
import time

MODEL_PATH = os.path.join(os.path.dirname(__file__), "vosk-model-en-in-0.5")

def transcribe_audio_offline(duration=30):
    """
    Offline audio transcription using Vosk.
    Returns transcript, timestamps, audio file path, and metadata.
    Compatible with Python 3.13 and avoids CFFI callback errors.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

    model = vosk.Model(MODEL_PATH)
    samplerate = 16000

    q = queue.Queue()
    audio_data = []

    # -------- FIXED CALLBACK (no .copy(), safe for Python 3.13) -------- #
    def callback(indata, frames, time_info, status):
        if status:
            print("SoundDevice Status:", status)

        # Convert raw buffer -> numpy array (safe & required for Py3.13)
        np_data = np.frombuffer(indata, dtype=np.int16)

        # Append to audio buffer list
        audio_data.append(np_data)

        # Also push raw bytes to Vosk queue
        q.put(bytes(indata))
    # ------------------------------------------------------------------ #

    print(f"🎙️ Recording for {duration} seconds...")

    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        dtype='int16',
        channels=1,
        callback=callback
    ):
        rec = vosk.KaldiRecognizer(model, samplerate)
        rec.SetWords(True)

        transcript_segments = []
        word_timestamps = []

        start_time = time.time()

        while time.time() - start_time < duration:
            try:
                data = q.get(timeout=0.5)

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    text = result.get("text", "").strip()

                    if text:
                        transcript_segments.append(text)

                    # Collect timestamps
                    if 'result' in result:
                        word_timestamps.extend(result['result'])

            except queue.Empty:
                continue

        # Final result
        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            transcript_segments.append(final_result["text"].strip())

        if 'result' in final_result:
            word_timestamps.extend(final_result['result'])

    print(f"✅ Recording completed ({duration}s)")

    # Combine everything into one transcript
    full_transcript = " ".join(transcript_segments).strip()
    if not full_transcript:
        full_transcript = "[No speech detected]"

    # Save transcript to file
    transcript_path = os.path.join(os.path.dirname(__file__), "transcript.txt")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(full_transcript)

    # -------- Save the recorded audio safely -------- #
    os.makedirs("audio_storage", exist_ok=True)

    if audio_data:
        audio_array = np.concatenate(audio_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = f"audio_storage/recording_{timestamp}.wav"

        sf.write(audio_path, audio_array, samplerate)
    else:
        audio_path = ""
    # ------------------------------------------------ #

    print(f"📝 Transcript: {full_transcript}")

    return {
        'transcript': full_transcript,
        'word_timestamps': word_timestamps,
        'audio_path': audio_path,
        'duration': duration
    }
