"""
Test AWS Credentials and Basic Connectivity
Tests S3 and Transcribe service access using environment variables
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
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

# Validate that credentials are loaded
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError(
        "AWS credentials not found. Please ensure .env file exists in backend/ directory with:\n"
        "  AWS_ACCESS_KEY_ID=your_key\n"
        "  AWS_SECRET_ACCESS_KEY=your_secret"
    )


def test_s3_connection():
    """Test S3 service connectivity"""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # List buckets to verify access
        response = s3_client.list_buckets()
        
        print("✅ S3 Connection: SUCCESS")
        
        # Print found buckets
        if response['Buckets']:
            for bucket in response['Buckets']:
                print(f"   Found bucket: {bucket['Name']}")
        
        return True
        
    except NoCredentialsError:
        print("❌ S3 Connection: FAILED - No credentials found")
        return False
    except ClientError as e:
        print(f"❌ S3 Connection: FAILED - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ S3 Connection: FAILED - {str(e)}")
        return False


def test_transcribe_connection():
    """Test AWS Transcribe service connectivity"""
    try:
        transcribe_client = boto3.client(
            'transcribe',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        
        # List transcription jobs to verify access
        response = transcribe_client.list_transcription_jobs(MaxResults=5)
        
        print("✅ Transcribe Connection: SUCCESS")
        
        # Print job count if any
        job_count = len(response.get('TranscriptionJobSummaries', []))
        print(f"   Found {job_count} transcription job(s)")
        
        return True
        
    except NoCredentialsError:
        print("❌ Transcribe Connection: FAILED - No credentials found")
        return False
    except ClientError as e:
        print(f"❌ Transcribe Connection: FAILED - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Transcribe Connection: FAILED - {str(e)}")
        return False


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Testing AWS Credentials...")
    print("="*60 + "\n")
    
    print(f"Region: {AWS_REGION}")
    print(f"Access Key: {AWS_ACCESS_KEY_ID[:8]}...\n")
    
    # Run tests
    s3_success = test_s3_connection()
    print()
    transcribe_success = test_transcribe_connection()
    
    # Summary
    print("\n" + "="*60)
    if s3_success and transcribe_success:
        print("✅ All AWS connections successful!")
    else:
        print("❌ Some connections failed. Check credentials and permissions.")
    print("="*60 + "\n")
    
    return s3_success and transcribe_success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

