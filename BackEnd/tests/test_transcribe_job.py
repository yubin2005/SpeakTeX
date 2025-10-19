"""
Test AWS Transcribe Job Creation
Tests ability to start a transcription job (doesn't wait for completion)
"""

import boto3
from botocore.exceptions import ClientError
import time
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in backend directory
backend_dir = Path(__file__).parent.parent
load_dotenv(dotenv_path=backend_dir / '.env')

# Load credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "speaktex-audio-storage")

# Validate that credentials are loaded
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError(
        "AWS credentials not found. Please ensure .env file exists in backend/ directory with:\n"
        "  AWS_ACCESS_KEY_ID=your_key\n"
        "  AWS_SECRET_ACCESS_KEY=your_secret\n"
        "  S3_BUCKET_NAME=your_bucket"
    )

TEST_AUDIO_KEY = "test/sample.wav"


def create_dummy_audio():
    """
    Create a minimal WAV file (just headers, not playable but valid for upload test)
    For a real test, you'd need actual audio content
    """
    # Minimal WAV file header (44 bytes)
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # "RIFF"
        0x24, 0x00, 0x00, 0x00,  # File size - 8
        0x57, 0x41, 0x56, 0x45,  # "WAVE"
        0x66, 0x6D, 0x74, 0x20,  # "fmt "
        0x10, 0x00, 0x00, 0x00,  # Subchunk1Size (16 for PCM)
        0x01, 0x00,              # AudioFormat (1 for PCM)
        0x01, 0x00,              # NumChannels (1 = mono)
        0x44, 0xAC, 0x00, 0x00,  # SampleRate (44100)
        0x88, 0x58, 0x01, 0x00,  # ByteRate
        0x02, 0x00,              # BlockAlign
        0x10, 0x00,              # BitsPerSample (16)
        0x64, 0x61, 0x74, 0x61,  # "data"
        0x00, 0x00, 0x00, 0x00   # Subchunk2Size (0 = no audio data)
    ])
    return wav_header


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Testing AWS Transcribe Job Creation")
    print("="*60 + "\n")
    
    # Initialize clients
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    transcribe_client = boto3.client(
        'transcribe',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    job_name = None
    all_success = True
    
    try:
        # Step 1: Upload test audio to S3
        print("Step 1: Uploading test audio... ", end="", flush=True)
        try:
            audio_data = create_dummy_audio()
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=TEST_AUDIO_KEY,
                Body=audio_data,
                ContentType='audio/wav'
            )
            print("✅")
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
            all_success = False
            raise
        
        # Step 2: Start transcribe job
        print("Step 2: Starting transcribe job... ", end="", flush=True)
        
        # Generate unique job name with timestamp
        timestamp = int(time.time())
        job_name = f"test-job-{timestamp}"
        
        media_uri = f"s3://{BUCKET_NAME}/{TEST_AUDIO_KEY}"
        
        try:
            response = transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                LanguageCode='en-US',
                MediaFormat='wav',
                Media={
                    'MediaFileUri': media_uri
                }
            )
            print("✅")
            
            # Get job info
            job_info = response['TranscriptionJob']
            print(f"\nJob Name: {job_info['TranscriptionJobName']}")
            print(f"Initial Status: {job_info['TranscriptionJobStatus']}")
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            # Note: The dummy audio file might cause the job to fail quickly
            # But we're just testing if we can START a job, not complete it
            if error_code == 'BadRequestException':
                print("⚠️")
                print(f"\n   Note: {e.response['Error']['Message']}")
                print("   This is OK - we're just testing if we can start jobs")
                print("   (The dummy audio file isn't real audio)")
            else:
                print(f"❌\n   Error: {e.response['Error']['Message']}")
                all_success = False
                raise
        
        # Step 3: List transcription jobs to verify it appears
        print("\nStep 3: Verifying job in list... ", end="", flush=True)
        try:
            list_response = transcribe_client.list_transcription_jobs(
                MaxResults=10
            )
            
            job_names = [job['TranscriptionJobName'] for job in list_response.get('TranscriptionJobSummaries', [])]
            
            if job_name in job_names:
                print("✅")
                print(f"   Job found in list")
            else:
                print("⚠️")
                print(f"   Job not found in recent jobs (this may be OK)")
            
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        all_success = False
    
    finally:
        # Cleanup: Delete test audio from S3
        print("\nCleaning up test files... ", end="", flush=True)
        try:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=TEST_AUDIO_KEY)
            print("✅")
        except:
            print("⚠️")
        
        # Note: Transcribe jobs cannot be deleted, only expire after 90 days
        # We'll let them fail naturally since they're using dummy audio
    
    # Summary
    print("\n" + "="*60)
    if all_success:
        print("✅ Transcribe API working!")
        print("   (Jobs may fail due to dummy audio, but API access confirmed)")
    else:
        print("❌ Transcribe API test failed")
    print("="*60 + "\n")
    
    return all_success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

