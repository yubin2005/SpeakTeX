"""
Lambda Function: Transcribe Audio from S3
Purpose: Start AWS Transcribe job and wait for completion
Input: S3 file key
Output: Transcribed text saved to BackEnd/AWSTranscribeResults/
"""

import os
import json
import sys
import time
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Load environment variables from BackEnd/.env
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)


def get_transcribe_client():
    """Create AWS Transcribe client"""
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-2')
    
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError("Missing AWS credentials in .env file")
    
    return boto3.client(
        'transcribe',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )


def start_transcription_job(s3_uri: str, job_name: str = None) -> dict:
    """
    Start AWS Transcribe job
    
    Args:
        s3_uri: S3 URI of audio file (s3://bucket/key)
        job_name: Optional job name (auto-generated if not provided)
        
    Returns:
        Dictionary with job information
    """
    transcribe_client = get_transcribe_client()
    
    # Generate job name if not provided
    if not job_name:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        job_name = f"speaktex_transcribe_{timestamp}"
    
    print(f"Starting transcription job: {job_name}")
    print(f"Audio file: {s3_uri}")
    
    try:
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': s3_uri},
            MediaFormat='webm',
            LanguageCode='en-US',
            OutputBucketName=os.environ.get('S3_BUCKET_NAME')
        )
        
        print(f"✓ Transcription job started successfully")
        
        return {
            'success': True,
            'job_name': job_name,
            'status': response['TranscriptionJob']['TranscriptionJobStatus']
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"✗ Failed to start transcription: [{error_code}] {error_message}")
        
        raise Exception(f"Transcription job failed: {error_message}")


def poll_transcription_job(job_name: str, max_wait_seconds: int = 300) -> dict:
    """
    Poll transcription job until completion
    
    Args:
        job_name: Transcription job name
        max_wait_seconds: Maximum time to wait (default 5 minutes)
        
    Returns:
        Dictionary with job results
    """
    transcribe_client = get_transcribe_client()
    
    print(f"\nPolling transcription job: {job_name}")
    print("This may take 30-60 seconds...")
    
    start_time = time.time()
    poll_interval = 5  # seconds
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait_seconds:
            raise TimeoutError(f"Transcription job exceeded {max_wait_seconds}s timeout")
        
        try:
            response = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            job = response['TranscriptionJob']
            status = job['TranscriptionJobStatus']
            
            print(f"  Status: {status} ({elapsed:.0f}s elapsed)")
            
            if status == 'COMPLETED':
                print(f"✓ Transcription completed successfully")
                
                # Get transcript URL
                transcript_uri = job['Transcript']['TranscriptFileUri']
                
                return {
                    'success': True,
                    'status': status,
                    'transcript_uri': transcript_uri,
                    'job_name': job_name
                }
                
            elif status == 'FAILED':
                failure_reason = job.get('FailureReason', 'Unknown error')
                print(f"✗ Transcription failed: {failure_reason}")
                
                raise Exception(f"Transcription failed: {failure_reason}")
                
            elif status == 'IN_PROGRESS':
                # Continue polling
                time.sleep(poll_interval)
                
            else:
                # Unknown status
                print(f"⚠ Unexpected status: {status}")
                time.sleep(poll_interval)
                
        except ClientError as e:
            error_message = e.response['Error']['Message']
            print(f"✗ Error checking job status: {error_message}")
            raise


def download_transcript(transcript_uri: str) -> dict:
    """
    Download and parse transcript JSON from S3 using boto3
    
    Args:
        transcript_uri: S3 URI or HTTPS URL of transcript
        
    Returns:
        Parsed transcript dictionary
    """
    print(f"\nDownloading transcript from S3...")
    
    try:
        # Parse the S3 URI to extract bucket and key
        # Format: https://s3.region.amazonaws.com/bucket-name/key
        # or: https://bucket-name.s3.region.amazonaws.com/key
        
        import re
        from urllib.parse import urlparse
        
        parsed = urlparse(transcript_uri)
        
        # Extract bucket and key from URL
        if '.s3.' in parsed.netloc or '.s3-' in parsed.netloc:
            # Format: bucket-name.s3.region.amazonaws.com/key
            bucket_name = parsed.netloc.split('.')[0]
            key = parsed.path.lstrip('/')
        else:
            # Format: s3.region.amazonaws.com/bucket-name/key
            path_parts = parsed.path.lstrip('/').split('/', 1)
            bucket_name = path_parts[0]
            key = path_parts[1] if len(path_parts) > 1 else ''
        
        print(f"  Bucket: {bucket_name}")
        print(f"  Key: {key}")
        
        # Create S3 client with credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-2')
        )
        
        # Download the transcript file
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        transcript_json = response['Body'].read().decode('utf-8')
        transcript_data = json.loads(transcript_json)
        
        print(f"✓ Transcript downloaded successfully from S3")
        
        return transcript_data
        
    except Exception as e:
        print(f"✗ Failed to download transcript: {str(e)}")
        raise


def extract_transcript_text(transcript_data: dict) -> str:
    """
    Extract transcribed text from AWS Transcribe result
    
    Args:
        transcript_data: Full transcript JSON from AWS
        
    Returns:
        Transcribed text as string
    """
    try:
        # AWS Transcribe result structure
        transcripts = transcript_data.get('results', {}).get('transcripts', [])
        
        if not transcripts:
            raise ValueError("No transcripts found in result")
        
        # Get the first transcript (combined result)
        text = transcripts[0].get('transcript', '')
        
        if not text:
            raise ValueError("Transcript text is empty")
        
        return text.strip()
        
    except Exception as e:
        print(f"✗ Error extracting transcript text: {str(e)}")
        raise


def convert_to_latex(transcript_text: str) -> str:
    """
    Convert transcript text to LaTeX using Gemini API
    
    Args:
        transcript_text: The transcribed speech text
        
    Returns:
        LaTeX code string
    """
    print(f"\nConverting transcript to LaTeX using Gemini API...")
    
    # Get Gemini API key from environment
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file")
    
    gemini_api_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent'
    
    prompt = f"""Convert this spoken mathematical expression into complete LaTeX code.

IMPORTANT FORMATTING RULES:
- For display equations (centered, large), wrap in $$...$$ (double dollar signs)
- For inline equations (small, in text), wrap in $...$ (single dollar signs)
- Use \\begin{{}} and \\end{{}} for matrices, aligned equations, cases, etc.
- Choose the most appropriate LaTeX format based on the expression complexity
- Include ALL necessary LaTeX delimiters in your output
- Return ONLY the LaTeX code, no explanations or markdown

Spoken expression: {transcript_text}"""
    
    request_body = {
        'contents': [{
            'parts': [{
                'text': prompt
            }]
        }],
        'generationConfig': {
            'temperature': 0.1,
            'maxOutputTokens': 2048
        }
    }
    
    try:
        response = requests.post(
            f"{gemini_api_url}?key={gemini_api_key}",
            headers={'Content-Type': 'application/json'},
            json=request_body,
            timeout=30
        )
        
        if not response.ok:
            error_data = response.json()
            raise Exception(f"Gemini API error: {response.status_code} - {error_data}")
        
        data = response.json()
        
        # Extract LaTeX from response
        latex_code = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        
        if not latex_code:
            raise Exception('No LaTeX code returned from Gemini API')
        
        # Clean up the response - remove markdown code blocks if present
        latex_code = latex_code.strip()
        latex_code = latex_code.replace('```latex', '').replace('```', '')
        latex_code = latex_code.strip()
        
        print(f"✓ LaTeX generated: {latex_code}")
        
        return latex_code
        
    except Exception as e:
        print(f"✗ Failed to convert to LaTeX: {str(e)}")
        raise


def save_transcript_result(transcript_data: dict, transcript_text: str, latex_code: str, job_name: str):
    """
    Save transcript results to BackEnd/AWSTranscribeResults/
    
    Args:
        transcript_data: Full transcript JSON
        transcript_text: Extracted text
        latex_code: Generated LaTeX code
        job_name: Transcription job name
    """
    # Create results directory if it doesn't exist
    results_dir = parent_dir / 'AWSTranscribeResults'
    results_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_transcript.json"
    filepath = results_dir / filename
    
    # Prepare result to save
    result = {
        'timestamp': timestamp,
        'job_name': job_name,
        'transcript_text': transcript_text,
        'latex_code': latex_code,
        'full_result': transcript_data
    }
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Results saved to: {filepath}")
    print(f"  Transcript: \"{transcript_text}\"")
    print(f"  LaTeX: \"{latex_code}\"")
    
    return str(filepath)


def transcribe_audio_from_s3(s3_file_key: str, bucket_name: str = None) -> dict:
    """
    Complete transcription workflow
    
    Args:
        s3_file_key: S3 object key (e.g., "audio/recordings/file.webm")
        bucket_name: S3 bucket name (defaults to env variable)
        
    Returns:
        Dictionary with transcript text and file path
    """
    # Get bucket name
    if not bucket_name:
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        if not bucket_name:
            raise ValueError("S3_BUCKET_NAME not set in .env file")
    
    # Construct S3 URI
    s3_uri = f"s3://{bucket_name}/{s3_file_key}"
    
    # Generate job name
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    job_name = f"speaktex_{timestamp}"
    
    # Step 1: Start transcription job
    start_result = start_transcription_job(s3_uri, job_name)
    
    # Step 2: Poll until completion
    poll_result = poll_transcription_job(job_name)
    
    # Step 3: Download transcript
    transcript_data = download_transcript(poll_result['transcript_uri'])
    
    # Step 4: Extract text
    transcript_text = extract_transcript_text(transcript_data)
    
    # Step 5: Convert to LaTeX using Gemini
    latex_code = convert_to_latex(transcript_text)
    
    # Step 6: Save results
    filepath = save_transcript_result(transcript_data, transcript_text, latex_code, job_name)
    
    return {
        'success': True,
        'transcript_text': transcript_text,
        'latex_code': latex_code,
        'filepath': filepath,
        'job_name': job_name
    }


def lambda_handler(event: dict, context=None) -> dict:
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event containing:
            - s3_file_key: S3 object key to transcribe
            - bucket_name: Optional S3 bucket name
        context: Lambda context object
        
    Returns:
        Response dictionary with statusCode and body
    """
    try:
        s3_file_key = event.get('s3_file_key')
        if not s3_file_key:
            raise ValueError("Missing required parameter: s3_file_key")
        
        bucket_name = event.get('bucket_name')
        
        print(f"Starting transcription workflow for: {s3_file_key}")
        
        # Run transcription
        result = transcribe_audio_from_s3(s3_file_key, bucket_name)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }
        
    except Exception as e:
        print(f"✗ Transcription workflow failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


if __name__ == '__main__':
    """
    Local testing entry point
    """
    import sys
    
    print("=" * 60)
    print("AWS Transcribe Audio Test")
    print("=" * 60)
    
    # Check for S3 file key argument
    if len(sys.argv) > 1:
        s3_file_key = sys.argv[1]
    else:
        print("\nUsage: python transcribe_audio.py <s3_file_key>")
        print("Example: python transcribe_audio.py audio/recordings/20241019_123456.webm")
        print("\nOr testing with most recent file from S3...")
        
        # Try to get most recent file
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                region_name=os.environ.get('AWS_REGION', 'us-east-2')
            )
            
            response = s3_client.list_objects_v2(
                Bucket=os.environ.get('S3_BUCKET_NAME'),
                Prefix='audio/recordings/'
            )
            
            if 'Contents' in response and len(response['Contents']) > 0:
                objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
                s3_file_key = objects[0]['Key']
                print(f"Found most recent file: {s3_file_key}")
            else:
                print("\n✗ No audio files found in S3")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            sys.exit(1)
    
    print()
    
    try:
        test_event = {
            's3_file_key': s3_file_key
        }
        
        response = lambda_handler(test_event)
        
        print("\n" + "=" * 60)
        if response['statusCode'] == 200:
            result = json.loads(response['body'])
            print("SUCCESS")
            print("=" * 60)
            print(f"\nTranscript: \"{result['transcript_text']}\"")
            print(f"\nSaved to: {result['filepath']}")
        else:
            print("FAILED")
            print("=" * 60)
            print(json.dumps(json.loads(response['body']), indent=2))
            sys.exit(1)
            
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(str(e))
        sys.exit(1)

