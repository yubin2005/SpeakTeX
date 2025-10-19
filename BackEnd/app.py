from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import boto3
import uuid
from datetime import datetime
import assemblyai as aai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

# Initialize AssemblyAI with API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# Initialize AWS S3 client
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
S3_BUCKET = os.getenv("S3_BUCKET")

s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def upload_to_s3(file_path, file_name):
    """Upload a file to S3 bucket"""
    if not s3_client or not S3_BUCKET:
        print("S3 client not configured or bucket not specified")
        return None
        
    try:
        # Generate a unique file name
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        s3_file_name = f"recordings/{timestamp}-{unique_id}-{file_name}"
        
        # Upload the file
        s3_client.upload_file(file_path, S3_BUCKET, s3_file_name)
        
        # Generate a URL for the uploaded file
        url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_file_name}"
        
        print(f"File uploaded to S3: {url}")
        return url
    except Exception as e:
        print(f"Error uploading to S3: {str(e)}")
        return None

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
        
        # Upload to S3 if configured
        s3_url = None
        if s3_client and S3_BUCKET:
            s3_url = upload_to_s3(temp_path, "recording.webm")
        
        # Transcribe using AssemblyAI
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(temp_path)
        
        # Prepare response
        response_data = {
            "transcript": transcript.text
        }
        
        # Add S3 URL if available
        if s3_url:
            response_data["audio_url"] = s3_url
        
        # Return the transcript text
        response = jsonify(response_data)
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