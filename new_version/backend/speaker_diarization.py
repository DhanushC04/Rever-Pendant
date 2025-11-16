"""
Complete Speaker Diarization with Pyannote.audio
Supports multiple speakers with detailed analysis
"""

import os
import torch
from models import get_db, Speaker, SpeakerSegment

# Check if pyannote is available
try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
    print("✅ Pyannote.audio loaded successfully")
except ImportError:
    PYANNOTE_AVAILABLE = False
    print("⚠️  Pyannote.audio not installed - using fallback mode")

class SpeakerDiarizer:
    """
    Speaker Diarization with Pyannote.audio
    Falls back to simple detection if pyannote not available
    """
    
    def __init__(self, use_auth_token=None):
        """
        Initialize speaker diarizer
        
        Args:
            use_auth_token: Hugging Face token (or set HUGGINGFACE_TOKEN env var)
        """
        self.pyannote_available = PYANNOTE_AVAILABLE
        self.pipeline = None
        
        if PYANNOTE_AVAILABLE:
            try:
                # Get token from parameter or environment
                token = use_auth_token or os.getenv('HUGGINGFACE_TOKEN')
                
                if not token:
                    print("⚠️  No Hugging Face token found")
                    print("   Set HUGGINGFACE_TOKEN in .env file")
                    print("   Falling back to simple speaker detection")
                    self.pyannote_available = False
                    return
                
                print("Loading pyannote pipeline...")
                self.pipeline = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=token
                )
                
                # Use GPU if available
                if torch.cuda.is_available():
                    print("✅ Using GPU for diarization")
                    self.pipeline.to(torch.device("cuda"))
                else:
                    print("ℹ️  Using CPU for diarization (slower)")
                
                print("✅ Pyannote pipeline ready")
                
            except Exception as e:
                print(f"⚠️  Failed to load pyannote: {e}")
                print("   Falling back to simple speaker detection")
                self.pyannote_available = False
                self.pipeline = None
    
    def diarize(self, audio_path):
        """
        Perform speaker diarization on audio file
        
        Args:
            audio_path: Path to audio file (.wav format)
            
        Returns:
            dict: {
                'speakers': [{'label': 'SPEAKER_00', 'total_duration': 15.5, ...}],
                'segments': [{'speaker': 'SPEAKER_00', 'start': 0.0, 'end': 5.2, ...}],
                'speaker_count': 2
            }
        """
        if not os.path.exists(audio_path):
            print(f"⚠️  Audio file not found: {audio_path}")
            return self._fallback_diarization()
        
        # Use pyannote if available
        if self.pyannote_available and self.pipeline:
            try:
                return self._pyannote_diarize(audio_path)
            except Exception as e:
                print(f"⚠️  Pyannote error: {e}")
                print("   Falling back to simple detection")
                return self._fallback_diarization()
        else:
            return self._fallback_diarization()
    
    def _pyannote_diarize(self, audio_path):
        """
        Real multi-speaker diarization using pyannote
        """
        print(f"🎭 Analyzing speakers in: {os.path.basename(audio_path)}")
        
        # Run diarization
        diarization = self.pipeline(audio_path)
        
        # Process results
        speakers_data = {}
        segments = []
        
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segment = {
                'speaker': speaker,
                'start': turn.start,
                'end': turn.end,
                'duration': turn.end - turn.start
            }
            segments.append(segment)
            
            # Accumulate speaker stats
            if speaker not in speakers_data:
                speakers_data[speaker] = {
                    'label': speaker,
                    'total_duration': 0,
                    'segment_count': 0
                }
            
            speakers_data[speaker]['total_duration'] += segment['duration']
            speakers_data[speaker]['segment_count'] += 1
        
        result = {
            'speakers': list(speakers_data.values()),
            'segments': segments,
            'speaker_count': len(speakers_data)
        }
        
        print(f"✅ Found {result['speaker_count']} speaker(s)")
        for speaker in result['speakers']:
            print(f"   - {speaker['label']}: {speaker['total_duration']:.1f}s ({speaker['segment_count']} segments)")
        
        return result
    
    def _fallback_diarization(self):
        """
        Simple fallback when pyannote not available
        Assumes single speaker
        """
        print("ℹ️  Using simplified speaker detection (single speaker)")
        
        return {
            'speakers': [{
                'label': 'SPEAKER_00',
                'total_duration': 30.0,
                'segment_count': 1
            }],
            'segments': [{
                'speaker': 'SPEAKER_00',
                'start': 0.0,
                'end': 30.0,
                'duration': 30.0
            }],
            'speaker_count': 1
        }
    
    def align_transcript_with_speakers(self, audio_path, transcript, word_timestamps):
        """
        Align transcribed words with speaker segments
        
        Args:
            audio_path: Path to audio file
            transcript: Full transcript text
            word_timestamps: List of {'word': str, 'start': float, 'end': float}
            
        Returns:
            list: [{'speaker': str, 'text': str, 'start': float, 'end': float}]
        """
        # Get speaker segments
        diarization_result = self.diarize(audio_path)
        segments = diarization_result['segments']
        
        if not word_timestamps:
            # No word timestamps - assign all text to first speaker
            if segments:
                return [{
                    'speaker': segments[0]['speaker'],
                    'text': transcript,
                    'start': segments[0]['start'],
                    'end': segments[0]['end']
                }]
            else:
                return [{
                    'speaker': 'SPEAKER_00',
                    'text': transcript,
                    'start': 0.0,
                    'end': 30.0
                }]
        
        # Match words to speakers based on timestamps
        speaker_transcripts = {}
        
        for word_data in word_timestamps:
            word = word_data.get('word', '')
            word_start = word_data.get('start', 0)
            word_end = word_data.get('end', 0)
            
            # Find which speaker was talking at this time
            matched_speaker = None
            for segment in segments:
                if segment['start'] <= word_start <= segment['end']:
                    matched_speaker = segment['speaker']
                    break
            
            # If no match, use first speaker
            if not matched_speaker and segments:
                matched_speaker = segments[0]['speaker']
            elif not matched_speaker:
                matched_speaker = 'SPEAKER_00'
            
            # Accumulate words for each speaker
            if matched_speaker not in speaker_transcripts:
                speaker_transcripts[matched_speaker] = {
                    'words': [],
                    'start': word_start,
                    'end': word_end
                }
            
            speaker_transcripts[matched_speaker]['words'].append(word)
            speaker_transcripts[matched_speaker]['end'] = max(
                speaker_transcripts[matched_speaker]['end'],
                word_end
            )
        
        # Format output
        formatted_transcript = []
        for speaker, data in speaker_transcripts.items():
            text = ' '.join(data['words'])
            formatted_transcript.append({
                'speaker': speaker,
                'text': text,
                'start': data['start'],
                'end': data['end']
            })
        
        return formatted_transcript
    
    def save_to_database(self, conversation_id, diarization_result, speaker_transcripts):
        """
        Save speaker data to database
        
        Args:
            conversation_id: ID of conversation
            diarization_result: Output from diarize()
            speaker_transcripts: Output from align_transcript_with_speakers()
            
        Returns:
            bool: Success status
        """
        db = get_db()
        
        try:
            print(f"💾 Saving speaker data for conversation {conversation_id}")
            
            # Save speakers
            speaker_map = {}  # Map speaker labels to database IDs
            
            for speaker_data in diarization_result['speakers']:
                speaker = Speaker(
                    conversation_id=conversation_id,
                    speaker_label=speaker_data['label'],
                    total_duration=speaker_data['total_duration']
                )
                db.add(speaker)
                db.flush()  # Get speaker ID
                
                speaker_map[speaker_data['label']] = speaker.id
                print(f"   - Saved {speaker_data['label']}: {speaker_data['total_duration']:.1f}s")
            
            # Save speaker segments with transcripts
            segment_count = 0
            for transcript_data in speaker_transcripts:
                speaker_label = transcript_data['speaker']
                speaker_id = speaker_map.get(speaker_label)
                
                if speaker_id:
                    segment = SpeakerSegment(
                        speaker_id=speaker_id,
                        start_time=transcript_data['start'],
                        end_time=transcript_data['end'],
                        text=transcript_data['text'],
                        confidence=0.85
                    )
                    db.add(segment)
                    segment_count += 1
            
            db.commit()
            print(f"✅ Saved {len(speaker_map)} speakers with {segment_count} segments")
            return True
        
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving speaker data: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            db.close()
    
    def get_speaker_statistics(self, diarization_result):
        """
        Get detailed statistics about speakers
        
        Returns:
            dict: Statistics for each speaker
        """
        stats = {}
        
        for speaker in diarization_result['speakers']:
            label = speaker['label']
            duration = speaker['total_duration']
            segment_count = speaker['segment_count']
            
            # Calculate average segment length
            avg_segment = duration / segment_count if segment_count > 0 else 0
            
            # Get segments for this speaker
            speaker_segments = [
                s for s in diarization_result['segments'] 
                if s['speaker'] == label
            ]
            
            # Calculate gaps (time between segments)
            gaps = []
            for i in range(len(speaker_segments) - 1):
                gap = speaker_segments[i+1]['start'] - speaker_segments[i]['end']
                if gap > 0:
                    gaps.append(gap)
            
            stats[label] = {
                'total_duration': duration,
                'segment_count': segment_count,
                'avg_segment_duration': avg_segment,
                'gaps': gaps,
                'avg_gap': sum(gaps) / len(gaps) if gaps else 0
            }
        
        return stats