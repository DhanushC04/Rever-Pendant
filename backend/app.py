from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time
import os

from face_module.recognize_face import recognize_face
from audio_module.transcribe_audio_offline import transcribe_audio_offline
from summary_module.summarize_text import summarize_text

app = Flask(__name__)

# Configure CORS for React development server
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Global state
process_state = {
    'stage': 'idle',
    'person': '',
    'transcript': '',
    'summary': '',
    'progress': 0,
    'logs': [],
    'error': '',
    'is_processing': False
}

def add_log(message, log_type='info'):
    """Add timestamped log entry"""
    timestamp = time.strftime('%H:%M:%S')
    process_state['logs'].append({
        'message': message,
        'type': log_type,
        'timestamp': timestamp
    })
    print(f"[{timestamp}] {message}")

def run_ai_pendant_process():
    """Execute complete AI Pendant pipeline"""
    global process_state
    
    try:
        process_state['is_processing'] = True
        process_state['stage'] = 'face'
        process_state['progress'] = 0
        process_state['error'] = ''
        process_state['logs'] = []
        
        add_log('🚀 AI Pendant System Starting...', 'success')
        
        # STAGE 1: Face Recognition
        add_log('📸 Initializing facial recognition...', 'info')
        person = recognize_face()
        process_state['person'] = person
        process_state['progress'] = 100
        add_log(f'✅ Person Detected: {person}', 'success')
        time.sleep(0.5)
        
        # STAGE 2: Audio Transcription
        process_state['stage'] = 'audio'
        process_state['progress'] = 0
        add_log('🎙️ Recording audio for 30 seconds...', 'info')
        
        # Progress simulation thread
        def simulate_audio_progress():
            for i in range(0, 101, 3):
                if process_state['stage'] == 'audio':
                    process_state['progress'] = i
                    time.sleep(0.15)
        
        progress_thread = threading.Thread(target=simulate_audio_progress)
        progress_thread.start()
        
        transcript = transcribe_audio_offline(duration=30)
        progress_thread.join()
        
        process_state['transcript'] = transcript
        process_state['progress'] = 100
        add_log('📝 Transcription completed successfully', 'success')
        time.sleep(0.5)
        
        # STAGE 3: AI Summarization
        process_state['stage'] = 'summary'
        process_state['progress'] = 0
        add_log('🤖 Generating Summary using BART model...', 'info')
        
        for i in range(0, 101, 20):
            process_state['progress'] = i
            time.sleep(0.25)
        
        summary = summarize_text(transcript)
        process_state['summary'] = summary
        process_state['progress'] = 100
        add_log('✨ Summary generated successfully', 'success')
        
        # Save results
        with open("final_output.txt", "w", encoding='utf-8') as f:
            f.write(f"Person: {person}\n")
            f.write(f"Transcript: {transcript}\n")
            f.write(f"Summary: {summary}\n")
        
        process_state['stage'] = 'complete'
        add_log('🎉 Process completed! Results saved.', 'success')
        
    except Exception as e:
        process_state['error'] = str(e)
        process_state['stage'] = 'idle'
        add_log(f'❌ Error: {str(e)}', 'error')
        print(f"ERROR: {e}")
    
    finally:
        process_state['is_processing'] = False

@app.route('/api/start', methods=['POST'])
def start_process():
    """Start AI Pendant process"""
    if process_state['is_processing']:
        return jsonify({'error': 'Process already running'}), 400
    
    thread = threading.Thread(target=run_ai_pendant_process)
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'message': 'Process initiated successfully'})

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
        'is_processing': False
    }
    return jsonify({'status': 'reset', 'message': 'Process reset successfully'})

@app.route('/api/download', methods=['GET'])
def download_results():
    """Download final output file"""
    if os.path.exists('final_output.txt'):
        return send_from_directory('.', 'final_output.txt', as_attachment=True)
    return jsonify({'error': 'No results available'}), 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 AI PENDANT SYSTEM - BACKEND SERVER")
    print("="*70)
    print("\n📡 API Endpoints Available:")
    print("   POST /api/start     - Start AI Pendant process")
    print("   GET  /api/status    - Get current status")
    print("   POST /api/reset     - Reset process")
    print("   GET  /api/download  - Download results")
    print("   GET  /api/health    - Health check")
    print("\n🌐 Server: http://localhost:5000")
    print("🔗 React Frontend: http://localhost:3000")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)