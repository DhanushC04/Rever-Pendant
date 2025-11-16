import sounddevice as sd
import numpy as np
import soundfile as sf
import time

def test_microphone(duration=5):
    """Test if microphone is working"""
    print("🎤 Testing microphone...")
    print(f"📊 Available audio devices:")
    print(sd.query_devices())
    
    samplerate = 16000
    print(f"\n🎙️ Recording for {duration} seconds...")
    
    try:
        # Record audio
        recording = sd.rec(int(duration * samplerate), 
                          samplerate=samplerate, 
                          channels=1, 
                          dtype='int16')
        
        # Wait for recording to finish
        sd.wait()
        
        print("✅ Recording complete!")
        
        # Save to file
        sf.write('test_recording.wav', recording, samplerate)
        print("💾 Saved as 'test_recording.wav'")
        print(f"📊 Audio shape: {recording.shape}")
        print(f"📊 Max amplitude: {np.max(np.abs(recording))}")
        
        if np.max(np.abs(recording)) < 100:
            print("⚠️ WARNING: Audio is very quiet! Check microphone volume.")
        else:
            print("✅ Microphone is working!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if microphone is plugged in")
        print("2. Check Windows sound settings")
        print("3. Try selecting a different device")

if __name__ == "__main__":
    test_microphone(duration=5)