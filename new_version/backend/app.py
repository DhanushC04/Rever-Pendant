"""
AI Pendant System - Complete Backend
Cross-Platform: Mac + Windows
Python 3.10+ Compatible
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import time
import os
import sys
import platform
from datetime import datetime
from pathlib import Path 

# Platform detection
IS_WINDOWS = platform.system() == 'Windows'
IS_MAC = platform.system() == 'Darwin'
print(f"🖥️  Running on: {platform.system()} ({platform.machine()})")

# YOUR ORIGINAL MODULES (unchanged)
from face_module.recognize_face import recognize_face
from audio_module.transcribe_audio_offline import transcribe_audio_offline
from summary_module.summarize_text import summarize_text

# NEW MODULES
from models import get_db, User, Conversation, Keynote, Reminder
from keynote_extraction import KeynoteExtractor
from location_service import LocationService
from audio_storage import AudioStorageManager
from rag_system import rag_system
from speaker_diarization import SpeakerDiarizer
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

# Email Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USERNAME', '')

mail = Mail(app)
scheduler = BackgroundScheduler()
scheduler.start()

# Initialize services
keynote_extractor = KeynoteExtractor()
location_service = LocationService()
audio_manager = AudioStorageManager()
diarizer = SpeakerDiarizer()

# Process state
process_state = {
    'stage': 'idle',
    'person': '',
    'transcript': '',
    'summary': '',
    'progress': 0,
    'logs': [],
    'error': '',
    'is_processing': False,
    'conversation_id': None,
    'speakers': [],
    'keynotes': []
}

def add_log(message, log_type='info'):
    """Add log message with timestamp"""
    timestamp = time.strftime('%H:%M:%S')
    process_state['logs'].append({
        'message': message,
        'type': log_type,
        'timestamp': timestamp
    })
    print(f"[{timestamp}] {message}")

def send_keynote_email(user_email, conversation_title, keynotes):
    """Send email with keynote summary"""
    add_log(f"📧 [KEYNOTE EMAIL] Starting - Target: {user_email}", 'info')
    
    # Ensure Flask app context for Message object creation and mail.send()
    with app.app_context():
        try:
            add_log(f"📧 [KEYNOTE EMAIL] Mail server config - Server: {app.config.get('MAIL_SERVER')}, Port: {app.config.get('MAIL_PORT')}", 'info')
            add_log(f"📧 [KEYNOTE EMAIL] Sender: {app.config.get('MAIL_USERNAME')}", 'info')
            
            msg = Message(
                subject=f"📋 Keynotes from: {conversation_title}",
                recipients=[user_email]
            )
            add_log(f"📧 [KEYNOTE EMAIL] Message object created with {len(keynotes)} keynotes", 'info')
            
            html_body = f"""
            <html>
            <body style="font-family: Arial; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #8b5cf6;">📋 Keynotes Summary</h1>
                    <h2>{conversation_title}</h2>
                    <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                    <hr>
                    <h3>Key Takeaways:</h3>
            """
            
            for i, keynote in enumerate(keynotes):
                add_log(f"📧 [KEYNOTE EMAIL] Processing keynote {i+1}: {keynote.get('category', 'unknown')}", 'info')
                color = {
                    'action_item': '#ef4444',
                    'decision': '#10b981',
                    'question': '#f59e0b',
                    'deadline': '#dc2626'
                }.get(keynote['category'], '#8b5cf6')
                
                html_body += f"""
                <div style="background: #f3f4f6; padding: 15px; margin: 10px 0; border-left: 4px solid {color}; border-radius: 8px;">
                    <span style="background: {color}; color: white; padding: 5px 10px; border-radius: 5px; font-size: 12px;">
                        {keynote['category'].replace('_', ' ').upper()}
                    </span>
                    <p>{keynote['content']}</p>
                    <p style="color: #6b7280; font-size: 12px;">Importance: {int(keynote['importance_score'] * 100)}%</p>
                </div>
                """
            
            html_body += """
                    <hr>
                    <p style="color: #6b7280; font-size: 12px;">
                        AI Pendant System - Automated Keynotes
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.html = html_body
            add_log(f"📧 [KEYNOTE EMAIL] HTML body built, calling mail.send()", 'info')
            
            mail.send(msg)
            add_log(f"✅ [KEYNOTE EMAIL] SUCCESS - Email sent to {user_email}", 'success')
            return True
        except Exception as e:
            add_log(f"❌ [KEYNOTE EMAIL] FAILED - Error: {str(e)}", 'error')
            import traceback
            add_log(f"❌ [KEYNOTE EMAIL] Traceback: {traceback.format_exc()}", 'error')
            return False

def send_reminder_email(reminder_id):
    """Send scheduled reminder"""
    add_log(f"⏰ [REMINDER EMAIL] Starting for reminder_id: {reminder_id}", 'info')
    
    # Scheduler jobs run outside request context — ensure app context
    with app.app_context():
        add_log(f"⏰ [REMINDER EMAIL] Inside app context, getting database", 'info')
        db = get_db()
        try:
            add_log(f"⏰ [REMINDER EMAIL] Querying reminder with ID: {reminder_id}", 'info')
            reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
            
            if not reminder:
                add_log(f"⏰ [REMINDER EMAIL] ERROR: Reminder {reminder_id} not found in database", 'error')
                return
            
            if reminder.is_sent:
                add_log(f"⏰ [REMINDER EMAIL] SKIP: Reminder {reminder_id} already sent at {reminder.sent_at}", 'info')
                return
            
            add_log(f"⏰ [REMINDER EMAIL] Reminder found, querying keynote: {reminder.keynote_id}", 'info')
            keynote = db.query(Keynote).filter(Keynote.id == reminder.keynote_id).first()
            
            add_log(f"⏰ [REMINDER EMAIL] Querying user: {reminder.user_id}", 'info')
            user = db.query(User).filter(User.id == reminder.user_id).first()
            
            if not keynote:
                add_log(f"⏰ [REMINDER EMAIL] ERROR: Keynote {reminder.keynote_id} not found", 'error')
                return
            
            if not user:
                add_log(f"⏰ [REMINDER EMAIL] ERROR: User {reminder.user_id} not found", 'error')
                return
            
            add_log(f"⏰ [REMINDER EMAIL] Found keynote '{keynote.category}' for user '{user.email}'", 'info')
            add_log(f"⏰ [REMINDER EMAIL] Mail config - Server: {app.config.get('MAIL_SERVER')}, Sender: {app.config.get('MAIL_USERNAME')}", 'info')
            
            msg = Message(
                subject=f"⏰ Reminder: {keynote.category.replace('_', ' ').title()}",
                recipients=[user.email]
            )
            add_log(f"⏰ [REMINDER EMAIL] Message object created for {user.email}", 'info')
            
            msg.html = f"""
            <html>
            <body style="padding: 20px; font-family: Arial;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #8b5cf6;">⏰ Reminder</h1>
                    <div style="background: #fef3c7; padding: 20px; border-left: 4px solid #f59e0b; border-radius: 8px;">
                        <h3>{keynote.category.replace('_', ' ').title()}</h3>
                        <p style="font-size: 16px;">{keynote.content}</p>
                        <p style="color: #6b7280; font-size: 12px;">Importance: {int(keynote.importance_score * 100)}%</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            add_log(f"⏰ [REMINDER EMAIL] HTML body built, calling mail.send()", 'info')
            mail.send(msg)
            
            add_log(f"⏰ [REMINDER EMAIL] mail.send() completed, updating database", 'info')
            reminder.is_sent = True
            reminder.sent_at = datetime.now()
            db.commit()
            add_log(f"✅ [REMINDER EMAIL] SUCCESS - Reminder {reminder_id} sent to {user.email} for keynote {keynote.id}", 'success')
            
        except Exception as e:
            add_log(f"❌ [REMINDER EMAIL] FAILED - Error: {str(e)}", 'error')
            import traceback
            add_log(f"❌ [REMINDER EMAIL] Traceback: {traceback.format_exc()}", 'error')
        finally:
            db.close()
            add_log(f"⏰ [REMINDER EMAIL] Database connection closed", 'info')

def run_ai_pendant_process(user_id=1):
    """Main process - runs your original + new features"""
    global process_state
    
    try:
        process_state['is_processing'] = True
        process_state['stage'] = 'face'
        process_state['progress'] = 0
        process_state['conversation_id'] = None
        process_state['speakers'] = []
        process_state['keynotes'] = []
        
        add_log('🚀 AI Pendant System Starting...', 'success')
        
        # STAGE 1: Face Recognition (YOUR ORIGINAL CODE)
        add_log('📸 Initializing facial recognition...', 'info')
        person = recognize_face()
        process_state['person'] = person
        process_state['progress'] = 100
        add_log(f'✅ Person Detected: {person}', 'success')
        time.sleep(0.5)
        
        # STAGE 2: Audio Transcription (YOUR ORIGINAL CODE)
        process_state['stage'] = 'audio'
        process_state['progress'] = 0
        add_log('🎙️ Recording audio...', 'info')
        
        result = transcribe_audio_offline(duration=30)
        
        # Handle both old (string) and new (dict) return format
        if isinstance(result, dict):
            transcript = result['transcript']
            audio_path = result.get('audio_path', '')
            word_timestamps = result.get('word_timestamps', [])
            duration = result.get('duration', 30)
        else:
            # Backward compatible with old string return
            transcript = result
            audio_path = ''
            word_timestamps = []
            duration = 30
        
        process_state['transcript'] = transcript
        process_state['progress'] = 100
        add_log('📝 Transcription completed', 'success')
        
        # Get location
        location_data = location_service.get_location_from_ip()
        location_str = location_service.format_location(location_data)
        add_log(f'📍 Location: {location_str}', 'info')
        
        # Save to database
        db = get_db()
        conversation = Conversation(
            user_id=user_id,
            title=f"Conversation - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            audio_path=audio_path,
            transcript=transcript,
            duration=duration,
            word_count=len(transcript.split()),
            location=location_str
        )
        db.add(conversation)
        db.commit()
        
        conversation_id = conversation.id
        process_state['conversation_id'] = conversation_id
        add_log(f'💾 Conversation saved (ID: {conversation_id})', 'success')
        db.close()
        
        # Speaker Diarization (optional, graceful fallback)
        if audio_path and os.path.exists(audio_path):
            add_log('🎭 Analyzing speakers...', 'info')
            try:
                diarization_result = diarizer.diarize(audio_path)
                speaker_transcripts = diarizer.align_transcript_with_speakers(
                    audio_path, transcript, word_timestamps
                )
                
                diarizer.save_to_database(conversation_id, diarization_result, speaker_transcripts)
                
                process_state['speakers'] = diarization_result['speakers']
                add_log(f'✅ Found {diarization_result["speaker_count"]} speaker(s)', 'success')
                
                # Update conversation
                db = get_db()
                conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                conv.speaker_count = diarization_result['speaker_count']
                db.commit()
                db.close()
            except Exception as e:
                add_log(f'⚠️ Speaker detection skipped: {str(e)}', 'warning')
        
        # STAGE 3: Summarization (YOUR ORIGINAL CODE)
        process_state['stage'] = 'summary'
        process_state['progress'] = 0
        add_log('🤖 Generating AI summary...', 'info')
        
        for i in range(0, 101, 20):
            process_state['progress'] = i
            time.sleep(0.25)
        
        summary = summarize_text(transcript)
        process_state['summary'] = summary
        add_log('✨ Summary generated', 'success')
        
        # Update conversation with summary
        db = get_db()
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        conv.summary = summary
        db.commit()
        db.close()
        
        # Extract keynotes
        add_log('🔑 Extracting keynotes...', 'info')
        keynotes = keynote_extractor.extract_keynotes(transcript, conversation_id)
        process_state['keynotes'] = keynotes
        add_log(f'✅ Extracted {len(keynotes)} keynotes', 'success')
        
        # Add to RAG system
        add_log('🧠 Adding to knowledge base...', 'info')
        rag_system.add_conversation_to_index(conversation_id, transcript)
        
        # Send email if configured
        if app.config['MAIL_USERNAME']:
            db = get_db()
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.email:
                add_log('📧 Sending email summary...', 'info')
                try:
                    send_keynote_email(user.email, conversation.title, keynotes)
                    add_log('✅ Email sent successfully', 'success')
                except Exception as e:
                    add_log(f'⚠️ Email failed: {str(e)}', 'warning')
            db.close()
        
        # Save to file (YOUR ORIGINAL OUTPUT - still works!)
        output_path = Path('final_output.txt')
        with open(output_path, "w", encoding='utf-8') as f:
            f.write(f"Person: {person}\n")
            f.write(f"Location: {location_str}\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Platform: {platform.system()}\n")
            f.write(f"\nTranscript:\n{transcript}\n")
            f.write(f"\nSummary:\n{summary}\n")
            f.write(f"\nKeynotes:\n")
            for i, keynote in enumerate(keynotes, 1):
                f.write(f"{i}. [{keynote['category']}] {keynote['content']}\n")
        
        process_state['stage'] = 'complete'
        process_state['progress'] = 100
        add_log('🎉 Process completed! All data saved.', 'success')
        
    except Exception as e:
        process_state['error'] = str(e)
        process_state['stage'] = 'idle'
        add_log(f'❌ Error: {str(e)}', 'error')
        import traceback
        traceback.print_exc()
    
    finally:
        process_state['is_processing'] = False

# =============================================================================
# API ROUTES
# =============================================================================

@app.route('/api/start', methods=['POST'])
def start_process():
    """Start AI Pendant process"""
    if process_state['is_processing']:
        return jsonify({'error': 'Process already running'}), 400
    
    data = request.json or {}
    user_id = data.get('user_id', 1)
    
    thread = threading.Thread(target=run_ai_pendant_process, args=(user_id,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started'})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current process status"""
    return jsonify(process_state)

@app.route('/api/reset', methods=['POST'])
def reset_process():
    """Reset process state"""
    global process_state
    if process_state['is_processing']:
        return jsonify({'error': 'Cannot reset while processing'}), 400
    
    process_state = {
        'stage': 'idle',
        'person': '',
        'transcript': '',
        'summary': '',
        'progress': 0,
        'logs': [],
        'error': '',
        'is_processing': False,
        'conversation_id': None,
        'speakers': [],
        'keynotes': []
    }
    return jsonify({'status': 'reset'})

@app.route('/api/download', methods=['GET'])
def download_results():
    """Download final output file"""
    output_path = Path('final_output.txt')
    if output_path.exists():
        return send_from_directory('.', 'final_output.txt', as_attachment=True)
    return jsonify({'error': 'No results available'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'platform': platform.system(),
        'python_version': sys.version
    })

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Get all conversations"""
    db = get_db()
    conversations = db.query(Conversation).order_by(
        Conversation.timestamp.desc()
    ).limit(50).all()
    
    result = [{
        'id': c.id,
        'title': c.title,
        'summary': c.summary,
        'duration': c.duration,
        'word_count': c.word_count,
        'speaker_count': c.speaker_count,
        'location': c.location,
        'timestamp': c.timestamp.isoformat()
    } for c in conversations]
    
    db.close()
    return jsonify(result)

@app.route('/api/conversations/<int:conv_id>', methods=['GET'])
def get_conversation_detail(conv_id):
    """Get detailed conversation"""
    db = get_db()
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    
    if not conv:
        db.close()
        return jsonify({'error': 'Not found'}), 404
    
    # Get speakers
    speakers_data = []
    for speaker in conv.speakers:
        segments = [{
            'start': seg.start_time,
            'end': seg.end_time,
            'text': seg.text
        } for seg in speaker.segments]
        
        speakers_data.append({
            'label': speaker.speaker_label,
            'name': speaker.speaker_name,
            'total_duration': speaker.total_duration,
            'segments': segments
        })
    
    # Get keynotes
    keynotes_data = keynote_extractor.get_keynotes_by_conversation(conv_id)
    
    result = {
        'id': conv.id,
        'title': conv.title,
        'transcript': conv.transcript,
        'summary': conv.summary,
        'duration': conv.duration,
        'location': conv.location,
        'timestamp': conv.timestamp.isoformat(),
        'speakers': speakers_data,
        'keynotes': keynotes_data
    }
    
    db.close()
    return jsonify(result)

@app.route('/api/keynotes/<int:keynote_id>/complete', methods=['POST'])
def mark_keynote_complete(keynote_id):
    """Toggle keynote completion"""
    db = get_db()
    keynote = db.query(Keynote).filter(Keynote.id == keynote_id).first()
    
    if not keynote:
        db.close()
        return jsonify({'error': 'Not found'}), 404
    
    keynote.is_completed = not keynote.is_completed
    db.commit()
    db.close()
    
    return jsonify({'status': 'updated', 'is_completed': keynote.is_completed})

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    """Create a reminder for a keynote"""
    add_log(f"⏰ [CREATE REMINDER] Request received", 'info')
    
    data = request.json
    keynote_id = data.get('keynote_id')
    reminder_time_str = data.get('reminder_time')
    user_id = data.get('user_id', 1)
    
    add_log(f"⏰ [CREATE REMINDER] Keynote ID: {keynote_id}, User ID: {user_id}, Time: {reminder_time_str}", 'info')
    
    if not keynote_id or not reminder_time_str:
        add_log(f"⏰ [CREATE REMINDER] ERROR: Missing keynote_id or reminder_time", 'error')
        return jsonify({'error': 'Missing data'}), 400
    
    try:
        reminder_time = datetime.fromisoformat(reminder_time_str.replace('Z', ''))
        add_log(f"⏰ [CREATE REMINDER] Parsed reminder_time: {reminder_time}", 'info')
    except Exception as e:
        add_log(f"⏰ [CREATE REMINDER] ERROR: Invalid datetime format - {str(e)}", 'error')
        return jsonify({'error': 'Invalid datetime'}), 400
    
    try:
        db = get_db()
        add_log(f"⏰ [CREATE REMINDER] Database connection established", 'info')
        
        reminder = Reminder(
            user_id=user_id,
            keynote_id=keynote_id,
            reminder_time=reminder_time
        )
        add_log(f"⏰ [CREATE REMINDER] Reminder object created", 'info')
        
        db.add(reminder)
        db.commit()
        reminder_id = reminder.id
        db.close()
        add_log(f"⏰ [CREATE REMINDER] Reminder saved to database with ID: {reminder_id}", 'success')
        
        # Schedule email
        add_log(f"⏰ [CREATE REMINDER] Scheduling background job for {reminder_time}", 'info')
        try:
            scheduler.add_job(
                func=send_reminder_email,
                trigger='date',
                run_date=reminder_time,
                args=[reminder_id],
                id=f"reminder_{reminder_id}"
            )
            add_log(f"✅ [CREATE REMINDER] Job scheduled successfully - ID: reminder_{reminder_id}", 'success')
        except Exception as sched_err:
            add_log(f"❌ [CREATE REMINDER] Scheduler error: {str(sched_err)}", 'error')
            return jsonify({'error': f'Scheduler error: {str(sched_err)}'}), 500
        
        return jsonify({
            'status': 'scheduled',
            'reminder_id': reminder_id,
            'reminder_time': reminder_time.isoformat()
        })
    except Exception as e:
        add_log(f"❌ [CREATE REMINDER] FAILED - {str(e)}", 'error')
        import traceback
        add_log(f"❌ [CREATE REMINDER] Traceback: {traceback.format_exc()}", 'error')
        return jsonify({'error': str(e)}), 500

@app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
def cancel_reminder(reminder_id):
    """Cancel a scheduled reminder"""
    db = get_db()
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        db.close()
        return jsonify({'error': 'Not found'}), 404
    
    try:
        scheduler.remove_job(f"reminder_{reminder_id}")
    except:
        pass
    
    db.delete(reminder)
    db.commit()
    db.close()
    
    return jsonify({'status': 'cancelled'})

@app.route('/api/reminders/user/<int:user_id>', methods=['GET'])
def get_user_reminders(user_id):
    """Get all reminders for a user"""
    db = get_db()
    reminders = db.query(Reminder).filter(Reminder.user_id == user_id).all()
    
    result = [{
        'id': r.id,
        'keynote_id': r.keynote_id,
        'reminder_time': r.reminder_time.isoformat(),
        'is_sent': r.is_sent,
        'sent_at': r.sent_at.isoformat() if r.sent_at else None
    } for r in reminders]
    
    db.close()
    return jsonify(result)

@app.route('/api/debug/reminders', methods=['GET'])
def debug_reminders():
    """Debug endpoint - show all scheduled reminder jobs and database records"""
    add_log(f"🔍 [DEBUG REMINDERS] Request received", 'info')
    
    try:
        # Get scheduler jobs
        jobs = scheduler.get_jobs()
        scheduled_jobs = []
        for job in jobs:
            if 'reminder_' in str(job.id):
                scheduled_jobs.append({
                    'job_id': str(job.id),
                    'next_run_time': str(job.next_run_time),
                    'trigger': str(job.trigger),
                    'func': str(job.func_ref)
                })
        
        add_log(f"🔍 [DEBUG REMINDERS] Found {len(scheduled_jobs)} scheduled reminder jobs", 'info')
        
        # Get database records
        db = get_db()
        all_reminders = db.query(Reminder).all()
        db_reminders = []
        for r in all_reminders:
            db_reminders.append({
                'id': r.id,
                'user_id': r.user_id,
                'keynote_id': r.keynote_id,
                'reminder_time': r.reminder_time.isoformat(),
                'is_sent': r.is_sent,
                'sent_at': r.sent_at.isoformat() if r.sent_at else None,
                'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None
            })
        
        db.close()
        add_log(f"🔍 [DEBUG REMINDERS] Found {len(db_reminders)} reminders in database", 'info')
        
        return jsonify({
            'status': 'ok',
            'scheduled_jobs': scheduled_jobs,
            'database_records': db_reminders,
            'mail_configured': bool(app.config.get('MAIL_USERNAME')),
            'scheduler_running': scheduler.running,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        add_log(f"❌ [DEBUG REMINDERS] Error: {str(e)}", 'error')
        return jsonify({'error': str(e), 'timestamp': datetime.now().isoformat()}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_history():
    """RAG-based chat"""
    data = request.json
    query = data.get('query', '')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    response = rag_system.chat_with_history(query)
    return jsonify(response)

@app.route('/api/search', methods=['GET'])
def search_conversations():
    """Semantic search"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    db = get_db()
    detailed_results = []
    results = rag_system.semantic_search(query, limit=10)
    for result in results:
        conv = db.query(Conversation).filter(
            Conversation.id == result['conversation_id']
        ).first()
        
        if conv:
            detailed_results.append({
                'id': conv.id,
                'title': conv.title,
                'summary': conv.summary,
                'timestamp': conv.timestamp.isoformat(),
                'similarity_score': result['similarity_score']
            })
    
    db.close()
    return jsonify(detailed_results)

@app.route('/api/audio/<int:conv_id>/delete', methods=['DELETE'])
def delete_audio(conv_id):
    """Delete audio file but keep transcript"""
    db = get_db()
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    
    if not conv:
        db.close()
        return jsonify({'error': 'Not found'}), 404
    
    if conv.audio_path and audio_manager.delete_audio(conv.audio_path):
        conv.is_audio_deleted = True
        db.commit()
        db.close()
        return jsonify({'status': 'deleted'})
    
    db.close()
    return jsonify({'error': 'Audio not found'}), 404

# =============================================================================
# STARTUP
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 AI PENDANT SYSTEM - COMPLETE BACKEND")
    print("="*70)
    print(f"\n🖥️  Platform: {platform.system()} {platform.machine()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print("\n✅ YOUR ORIGINAL MODULES: Loaded")
    print("   - Face Recognition (face_module/)")
    print("   - Audio Transcription (audio_module/)")
    print("   - Summarization (summary_module/)")
    print("\n🆕 NEW FEATURES: Ready")
    print("   - Database Storage")
    print("   - Keynote Extraction")
    print("   - Email & Reminders")
    print("   - RAG Chat")
    print("   - Semantic Search")
    print("\n🌐 Server starting on: http://localhost:5000")
    print("="*70 + "\n")
    
    # Initialize database
    from models import Base, engine
    Base.metadata.create_all(engine)
    print("✅ Database initialized\n")
    
    # Start server
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)


if __name__ == '__main__':
    # Initialize database
    from models import Base, engine
    Base.metadata.create_all(engine)
    print("✅ Database initialized\n")
    
    # Start server
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)