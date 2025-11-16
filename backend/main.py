from face_module.recognize_face import recognize_face
from audio_module.transcribe_audio_offline import transcribe_audio_offline
from summary_module.summarize_text import summarize_text

def main():
    print("\n🚀 AI Pendant System Starting...\n")

    # STEP 1: Facial Recognition
    person = recognize_face()
    print(f"👤 Person Detected: {person}")

    # STEP 2: Audio Transcription
    transcript = transcribe_audio_offline(duration=30)
    print(f"🎧 Transcript: {transcript}")

    # STEP 3: Summarization
    summary = summarize_text(transcript)
    print(f"📝 Summary: {summary}")

    # STEP 4: Save Results
    with open("final_output.txt", "w") as f:
        f.write(f"Person: {person}\n")
        f.write(f"Transcript: {transcript}\n")
        f.write(f"Summary: {summary}\n")

if __name__ == "__main__":
    main()
