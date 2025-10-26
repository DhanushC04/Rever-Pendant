import os
import queue
import sounddevice as sd
import vosk
import json

MODEL_PATH = r"C:\Users\User\Downloads\Capstone-master\Capstone-master\audio_module\vosk-model-en-in-0.5"

def transcribe_audio_offline(duration=30):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")

    model = vosk.Model(MODEL_PATH)
    samplerate = 16000
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status)
        q.put(bytes(indata))

    print(f"🎙️ Recording for {duration} seconds...")
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        transcript = []

        for _ in range(int(duration * samplerate / 8000)):
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    transcript.append(text)

        final_result = json.loads(rec.FinalResult())
        if final_result.get("text"):
            transcript.append(final_result["text"].strip())

    full_transcript = " ".join(transcript).strip()

    if not full_transcript:
        full_transcript = "[No speech detected]"

    with open("audio_module/transcript.txt", "w") as f:
        f.write(full_transcript)

    print(f"📝 Transcript: {full_transcript}")
    return full_transcript
