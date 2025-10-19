"""
Test S3 Upload and Download Operations
Tests basic S3 file operations: upload, download, verify, delete
"""

import boto3
from botocore.exceptions import ClientError
import tempfile
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

TEST_KEY = "test/hello.txt"
TEST_CONTENT = "Hello SpeakTeX! This is a test file."


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Testing S3 Operations")
    print("="*60 + "\n")
    
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Test Key: {TEST_KEY}\n")
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    test_file_path = None
    download_file_path = None
    all_success = True
    
    try:
        # Step 1: Create test file
        print("Step 1: Creating test file... ", end="", flush=True)
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write(TEST_CONTENT)
            test_file_path = f.name
        print("✅")
        
        # Step 2: Upload to S3
        print("Step 2: Uploading to S3... ", end="", flush=True)
        try:
            s3_client.upload_file(
                test_file_path,
                BUCKET_NAME,
                TEST_KEY,
                ExtraArgs={'ContentType': 'text/plain'}
            )
            print("✅")
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
            all_success = False
            raise
        
        # Step 3: Download from S3
        print("Step 3: Downloading from S3... ", end="", flush=True)
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
                download_file_path = f.name
            
            s3_client.download_file(BUCKET_NAME, TEST_KEY, download_file_path)
            print("✅")
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
            all_success = False
            raise
        
        # Step 4: Verify content
        print("Step 4: Verifying content... ", end="", flush=True)
        with open(download_file_path, 'r') as f:
            downloaded_content = f.read()
        
        if downloaded_content == TEST_CONTENT:
            print("✅")
        else:
            print("❌")
            print(f"   Expected: {TEST_CONTENT}")
            print(f"   Got: {downloaded_content}")
            all_success = False
        
        # Step 5: Cleanup - Delete from S3
        print("Step 5: Cleaning up... ", end="", flush=True)
        try:
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=TEST_KEY)
            print("✅")
        except ClientError as e:
            print(f"❌\n   Error: {e.response['Error']['Message']}")
            all_success = False
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        all_success = False
        
        # Try to cleanup even if test failed
        try:
            print("\nAttempting cleanup after error... ", end="", flush=True)
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=TEST_KEY)
            print("✅")
        except:
            print("❌ (File may not exist)")
    
    finally:
        # Clean up local files
        if test_file_path and os.path.exists(test_file_path):
            os.unlink(test_file_path)
        if download_file_path and os.path.exists(download_file_path):
            os.unlink(download_file_path)
    
    # Summary
    print("\n" + "="*60)
    if all_success:
        print("✅ All S3 operations working!")
    else:
        print("❌ Some S3 operations failed")
    print("="*60 + "\n")
    
    return all_success


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

