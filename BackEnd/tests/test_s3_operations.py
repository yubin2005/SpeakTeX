"""
Test Real Audio File Upload to S3
Tests uploading an actual .webm audio file to the audio/ directory
"""

import boto3
from botocore.exceptions import ClientError
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

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

# Your actual audio file path
AUDIO_FILE_PATH = r"F:\SpeakTex\BackEnd\temp_audio.webm"


def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("Testing Real Audio File Upload to S3")
    print("="*70 + "\n")
    
    # Step 0: Check if file exists
    print("Step 0: Checking if audio file exists... ", end="", flush=True)
    if not os.path.exists(AUDIO_FILE_PATH):
        print("❌")
        print(f"\n   Error: File not found at {AUDIO_FILE_PATH}")
        print("   Please ensure the file exists at this location.\n")
        return False
    
    file_size = os.path.getsize(AUDIO_FILE_PATH)
    print("✅")
    print(f"   File: {AUDIO_FILE_PATH}")
    print(f"   Size: {format_file_size(file_size)}\n")
    
    # Initialize S3 client
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Region: {AWS_REGION}\n")
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    # Generate S3 key with timestamp (matching your backend logic)
    timestamp = int(datetime.now().timestamp() * 1000)
    s3_key = f"audio/{timestamp}_temp_audio.webm"
    
    all_success = True
    
    try:
        # Step 1: Upload to S3
        print("Step 1: Uploading audio file to S3... ", end="", flush=True)
        try:
            s3_client.upload_file(
                AUDIO_FILE_PATH,
                BUCKET_NAME,
                s3_key,
                ExtraArgs={
                    'ContentType': 'audio/webm',
                    'Metadata': {
                        'original-filename': 'temp_audio.webm',
                        'upload-timestamp': str(timestamp)
                    }
                }
            )
            print("✅")
            print(f"   Uploaded to: s3://{BUCKET_NAME}/{s3_key}")
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
            all_success = False
            raise
        
        # Step 2: Verify file exists in S3
        print("\nStep 2: Verifying file in S3... ", end="", flush=True)
        try:
            response = s3_client.head_object(Bucket=BUCKET_NAME, Key=s3_key)
            s3_size = response['ContentLength']
            print("✅")
            print(f"   S3 Size: {format_file_size(s3_size)}")
            print(f"   Content-Type: {response.get('ContentType', 'N/A')}")
            print(f"   Last Modified: {response.get('LastModified', 'N/A')}")
            
            # Verify size matches
            if s3_size == file_size:
                print("   ✅ File size matches!")
            else:
                print(f"   ⚠️  Size mismatch: Local={format_file_size(file_size)}, S3={format_file_size(s3_size)}")
                
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
            all_success = False
        
        # Step 3: List files in audio/ directory
        print("\nStep 3: Listing files in audio/ directory... ", end="", flush=True)
        try:
            response = s3_client.list_objects_v2(
                Bucket=BUCKET_NAME,
                Prefix='audio/',
                MaxKeys=10
            )
            
            if 'Contents' in response:
                file_count = len(response['Contents'])
                print(f"✅ Found {file_count} file(s)")
                print("\n   Recent files:")
                for obj in response['Contents'][:5]:  # Show max 5 files
                    print(f"   - {obj['Key']} ({format_file_size(obj['Size'])})")
            else:
                print("✅ (Directory empty)")
                
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
        
        # Step 4: Generate pre-signed URL for download/verification
        print("\nStep 4: Generating pre-signed URL... ", end="", flush=True)
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
                ExpiresIn=3600  # 1 hour
            )
            print("✅")
            print(f"\n   You can download the file using this URL (valid for 1 hour):")
            print(f"   {url[:80]}...")
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
        
        # Step 5: Ask if user wants to delete the test file
        print("\n" + "="*70)
        print("Upload successful! The file is now in S3.")
        print("="*70)
        
        delete_choice = input("\nDo you want to delete the test file from S3? (y/n): ").strip().lower()
        
        if delete_choice == 'y':
            print("\nStep 5: Deleting test file from S3... ", end="", flush=True)
            try:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
                print("✅")
                print("   File deleted successfully")
            except ClientError as e:
                print(f"❌\n   Error: {e.response['Error']['Message']}")
                all_success = False
        else:
            print("\n   File kept in S3. You can access it at:")
            print(f"   s3://{BUCKET_NAME}/{s3_key}")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        all_success = False
        
        # Try to cleanup even if test failed
        try:
            print("\nAttempting cleanup after error... ", end="", flush=True)
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
            print("✅")
        except:
            print("❌ (File may not exist)")
    
    # Summary
    print("\n" + "="*70)
    if all_success:
        print("✅ Audio file upload test passed!")
        print(f"\n   File location: s3://{BUCKET_NAME}/{s3_key}")
        print(f"   File size: {format_file_size(file_size)}")
    else:
        print("❌ Some operations failed")
    print("="*70 + "\n")
    
    return all_success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)