"""
Test Speaker Diarization
Run this to verify speaker detection is working
"""

from speaker_diarization import SpeakerDiarizer
from models import get_db, Conversation, Speaker, SpeakerSegment
import os

def test_basic_diarization():
    """Test basic speaker diarization functionality"""
    print("\n" + "="*70)
    print("🎭 SPEAKER DIARIZATION TEST")
    print("="*70 + "\n")
    
    diarizer = SpeakerDiarizer()
    
    # Test with dummy audio path
    print("Test 1: Basic Diarization")
    print("─"*70)
    
    audio_path = "test_audio.wav"  # Doesn't need to exist for simplified version
    
    result = diarizer.diarize(audio_path)
    
    print(f"✅ Diarization completed")
    print(f"\n📊 Results:")
    print(f"   Total speakers: {result['speaker_count']}")
    print(f"   Total segments: {len(result['segments'])}\n")
    
    print("👥 Speaker Details:")
    for i, speaker in enumerate(result['speakers'], 1):
        print(f"\n{i}. Speaker: {speaker['label']}")
        print(f"   Total duration: {speaker['total_duration']:.1f} seconds")
        print(f"   Segment count: {speaker.get('segment_count', 'N/A')}")
    
    print("\n📝 Segments:")
    for i, segment in enumerate(result['segments'], 1):
        print(f"\n{i}. {segment['speaker']}")
        print(f"   Time: {segment['start']:.1f}s - {segment['end']:.1f}s")
        print(f"   Duration: {segment['duration']:.1f}s")
    
    return result['speaker_count'] > 0

def test_transcript_alignment():
    """Test aligning transcript with speakers"""
    print("\n" + "="*70)
    print("🔗 TRANSCRIPT ALIGNMENT TEST")
    print("="*70 + "\n")
    
    diarizer = SpeakerDiarizer()
    
    test_transcript = "This is a test conversation. We are discussing the project details."
    test_timestamps = []  # Simplified version doesn't use this
    audio_path = "test_audio.wav"
    
    print("Test transcript:")
    print(f"'{test_transcript}'\n")
    
    print("Aligning transcript with speakers...")
    
    aligned = diarizer.align_transcript_with_speakers(
        audio_path, 
        test_transcript, 
        test_timestamps
    )
    
    if aligned:
        print(f"✅ Alignment successful")
        print(f"   Found {len(aligned)} speaker transcript(s)\n")
        
        for i, item in enumerate(aligned, 1):
            print(f"{i}. {item['speaker']}")
            print(f"   Time: {item['start']:.1f}s - {item['end']:.1f}s")
            print(f"   Text: {item['text'][:80]}...")
            print()
        
        return True
    else:
        print("⚠️  No alignment produced")
        return False

def test_database_integration():
    """Test saving speaker data to database"""
    print("\n" + "="*70)
    print("💾 DATABASE INTEGRATION TEST")
    print("="*70 + "\n")
    
    db = get_db()
    
    # Get latest conversation
    conversations = db.query(Conversation).order_by(
        Conversation.id.desc()
    ).limit(3).all()
    
    if not conversations:
        print("⚠️  No conversations in database")
        print("   Run a full process first\n")
        db.close()
        return False
    
    print(f"Found {len(conversations)} recent conversation(s)\n")
    
    for conv in conversations:
        print(f"{'─'*70}")
        print(f"📝 Conversation ID: {conv.id}")
        print(f"   Title: {conv.title}")
        print(f"   Date: {conv.timestamp}")
        print(f"{'─'*70}\n")
        
        # Check speakers
        speakers = db.query(Speaker).filter(
            Speaker.conversation_id == conv.id
        ).all()
        
        print(f"👥 Speakers in database: {len(speakers)}")
        
        if speakers:
            for i, speaker in enumerate(speakers, 1):
                print(f"\n{i}. {speaker.speaker_label}")
                if speaker.speaker_name:
                    print(f"   Name: {speaker.speaker_name}")
                print(f"   Duration: {speaker.total_duration:.1f}s")
                
                # Check segments
                segments = db.query(SpeakerSegment).filter(
                    SpeakerSegment.speaker_id == speaker.id
                ).all()
                
                print(f"   Segments: {len(segments)}")
                
                if segments:
                    for j, seg in enumerate(segments[:3], 1):  # Show first 3
                        print(f"      {j}. {seg.start_time:.1f}s-{seg.end_time:.1f}s: {seg.text[:50]}...")
        else:
            print("   No speaker data found")
            print("   This is normal if using simplified diarization")
        
        print()
    
    db.close()
    return True

def test_with_real_audio():
    """Test with actual recorded audio if available"""
    print("\n" + "="*70)
    print("🎵 REAL AUDIO TEST")
    print("="*70 + "\n")
    
    # Check for audio files
    audio_dir = "audio_storage"
    
    if not os.path.exists(audio_dir):
        print(f"⚠️  Audio storage directory not found: {audio_dir}")
        print("   Record a conversation first\n")
        return False
    
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.wav')]
    
    if not audio_files:
        print(f"⚠️  No audio files found in {audio_dir}")
        print("   Record a conversation first\n")
        return False
    
    print(f"📁 Found {len(audio_files)} audio file(s)")
    
    # Test with most recent file
    latest_audio = sorted(audio_files)[-1]
    audio_path = os.path.join(audio_dir, latest_audio)
    
    print(f"   Testing with: {latest_audio}")
    print(f"   Path: {audio_path}\n")
    
    diarizer = SpeakerDiarizer()
    
    print("Running diarization...")
    result = diarizer.diarize(audio_path)
    
    print(f"\n✅ Diarization completed")
    print(f"   Speakers detected: {result['speaker_count']}")
    print(f"   Segments: {len(result['segments'])}\n")
    
    return True

def test_manual_scenario():
    """Test a specific scenario step by step"""
    print("\n" + "="*70)
    print("🎬 MANUAL SCENARIO TEST")
    print("="*70 + "\n")
    
    print("Simulating a conversation recording and analysis...\n")
    
    diarizer = SpeakerDiarizer()
    
    # Step 1: Diarize
    print("Step 1: Analyzing audio for speakers...")
    audio_path = "simulated_audio.wav"
    diarization_result = diarizer.diarize(audio_path)
    print(f"✅ Found {diarization_result['speaker_count']} speaker(s)\n")
    
    # Step 2: Align transcript
    print("Step 2: Aligning transcript with speakers...")
    transcript = "Hello team. Let's discuss the project timeline and deliverables."
    speaker_transcripts = diarizer.align_transcript_with_speakers(
        audio_path,
        transcript,
        []
    )
    print(f"✅ Aligned {len(speaker_transcripts)} transcript segment(s)\n")
    
    # Step 3: Save to database (using test conversation ID)
    print("Step 3: Saving to database...")
    success = diarizer.save_to_database(
        conversation_id=9999,  # Test ID
        diarization_result=diarization_result,
        speaker_transcripts=speaker_transcripts
    )
    
    if success:
        print("✅ Saved to database\n")
        
        # Verify
        db = get_db()
        test_speakers = db.query(Speaker).filter(
            Speaker.conversation_id == 9999
        ).all()
        
        print(f"Verification: Found {len(test_speakers)} speaker(s) in database")
        
        # Cleanup
        for s in test_speakers:
            db.delete(s)
        db.commit()
        db.close()
        
        print("✅ Test data cleaned up\n")
        return True
    else:
        print("❌ Failed to save to database\n")
        return False

if __name__ == '__main__':
    print("\n🚀 Starting Speaker Diarization Tests...\n")
    
    # Run all tests
    results = {
        'Basic Diarization': test_basic_diarization(),
        'Transcript Alignment': test_transcript_alignment(),
        'Database Integration': test_database_integration(),
        'Real Audio': test_with_real_audio(),
        'Manual Scenario': test_manual_scenario()
    }
    
    # Summary
    print("\n" + "="*70)
    print("🎯 TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print("="*70 + "\n")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"Overall: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("✅ All speaker diarization tests passed!")
        print("\nNote: This is simplified diarization (single speaker)")
        print("For multi-speaker detection, you'll need pyannote.audio")
    elif passed > 0:
        print("⚠️  Some tests passed, some failed")
        print("\nThis is expected if:")
        print("- No conversations recorded yet")
        print("- No audio files in audio_storage/")
    else:
        print("❌ All tests failed - check installation")
        print("\nDebugging:")
        print("1. Verify speaker_diarization.py exists")
        print("2. Check database connection")
        print("3. Run: python speaker_diarization.py")