from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import assemblyai as aai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

# Initialize AssemblyAI with API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/api/transcribe', methods=['POST', 'OPTIONS'])
def transcribe_audio():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
        
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files['audio']
    
    if audio_file.filename == '':
        return jsonify({"error": "Empty audio file"}), 400
    
    try:
        # Save the audio file temporarily
        temp_path = "temp_audio.webm"
        audio_file.save(temp_path)
        
        # Transcribe using AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_path)
        
        # Return the transcript text
        response = jsonify({"transcript": transcript.text})
        return response, 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a route for testing CORS
@app.route('/api/test', methods=['GET', 'OPTIONS'])
def test_cors():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        return response
        
    response = jsonify({"message": "CORS is working!"})
    return response, 200

if __name__ == '__main__':
    app.run(debug=True)