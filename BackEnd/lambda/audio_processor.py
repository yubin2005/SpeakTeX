"""
Lambda Function: Audio Processor
Purpose: Processes audio files from S3, transcribes using Gemini API, converts to LaTeX
Trigger: S3 upload event
Output: Stores results back to S3 and optionally in DynamoDB
"""

import json
import os
import boto3
import tempfile
from typing import Dict, Any
import google.generativeai as genai

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Configure Gemini API
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function
    
    Args:
        event: S3 event containing bucket and object key information
        context: Lambda context object
        
    Returns:
        Response dictionary with status code and processing results
    """
    try:
        # Extract S3 event information
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        print(f"Processing audio file: {object_key} from bucket: {bucket_name}")
        
        # Download audio file from S3
        audio_data = download_audio_from_s3(bucket_name, object_key)
        
        # Process audio with Gemini API
        transcript = transcribe_audio(audio_data)
        latex_output = convert_to_latex(transcript)
        
        # Prepare result
        result = {
            'transcript': transcript,
            'latex': latex_output,
            'audio_key': object_key,
            'status': 'success'
        }
        
        # Store result back to S3
        result_key = object_key.replace('uploads/', 'results/').replace('.webm', '.json')
        store_result_to_s3(bucket_name, result_key, result)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'status': 'failed'
            })
        }


def download_audio_from_s3(bucket: str, key: str) -> bytes:
    """
    Download audio file from S3 bucket
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        Audio file content as bytes
    """
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()


def transcribe_audio(audio_data: bytes) -> str:
    """
    Transcribe audio using Gemini API
    
    Args:
        audio_data: Audio file content as bytes
        
    Returns:
        Transcribed text
    """
    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
        temp_audio.write(audio_data)
        temp_audio_path = temp_audio.name
    
    try:
        # Upload audio file to Gemini
        audio_file = genai.upload_file(path=temp_audio_path)
        
        # Configure model for transcription
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate transcription
        prompt = "Transcribe this audio accurately. Focus on mathematical expressions and technical terms."
        response = model.generate_content([prompt, audio_file])
        
        return response.text.strip()
        
    finally:
        # Clean up temporary file
        os.unlink(temp_audio_path)


def convert_to_latex(transcript: str) -> str:
    """
    Convert transcribed text to LaTeX format using Gemini API
    
    Args:
        transcript: Transcribed text from audio
        
    Returns:
        LaTeX formatted mathematical expression
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""Convert the following mathematical expression to LaTeX code. 
Return ONLY the LaTeX code without explanation or markdown formatting: {transcript}"""
    
    response = model.generate_content(prompt)
    latex_code = response.text.strip()
    
    # Remove markdown code blocks if present
    latex_code = latex_code.replace('```latex', '').replace('```', '').strip()
    
    return latex_code


def store_result_to_s3(bucket: str, key: str, result: Dict[str, Any]) -> None:
    """
    Store processing result to S3
    
    Args:
        bucket: S3 bucket name
        key: S3 object key for result
        result: Processing result dictionary
    """
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(result),
        ContentType='application/json'
    )
    print(f"Result stored to s3://{bucket}/{key}")

