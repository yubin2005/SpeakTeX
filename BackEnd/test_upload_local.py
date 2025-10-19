"""
Local Test Script: Upload temp_audio.webm to S3
Purpose: Test S3 upload functionality without deploying to Lambda
Usage: python test_upload_local.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add lambda directory to path
sys.path.insert(0, str(Path(__file__).parent / 'lambda'))

from upload_audio import upload_audio_to_s3, get_s3_client


def validate_environment():
    """
    Validate that all required environment variables are set
    
    Returns:
        Boolean indicating if environment is valid
    """
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'S3_BUCKET_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("✗ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease create a .env file in the BackEnd directory with these variables.")
        print("See .env.example for reference.")
        return False
    
    print("✓ All required environment variables are set")
    return True


def check_aws_connectivity():
    """
    Test AWS credentials and S3 connectivity
    
    Returns:
        Boolean indicating if AWS connection is successful
    """
    try:
        s3_client = get_s3_client()
        
        # Test credentials by listing buckets
        response = s3_client.list_buckets()
        
        print(f"✓ AWS credentials are valid")
        print(f"✓ Found {len(response['Buckets'])} S3 buckets")
        
        # Check if target bucket exists
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        bucket_exists = any(b['Name'] == bucket_name for b in response['Buckets'])
        
        if bucket_exists:
            print(f"✓ Target bucket '{bucket_name}' exists")
        else:
            print(f"⚠ Warning: Bucket '{bucket_name}' not found in your account")
            print(f"  Available buckets: {', '.join(b['Name'] for b in response['Buckets'][:5])}")
        
        return True
        
    except Exception as e:
        print(f"✗ AWS connection failed: {str(e)}")
        return False


def test_upload():
    """
    Main test function to upload temp_audio.webm to S3
    """
    print("=" * 70)
    print("SpeakTeX - S3 Upload Test")
    print("=" * 70)
    print()
    
    # Load environment variables
    print("Step 1: Loading environment variables...")
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print(f"✗ .env file not found at: {env_path}")
        print("  Please create a .env file. See .env.example for reference.")
        return
    
    load_dotenv(dotenv_path=env_path)
    print(f"✓ Loaded .env from: {env_path}")
    print()
    
    # Validate environment
    print("Step 2: Validating environment variables...")
    if not validate_environment():
        return
    print()
    
    # Test AWS connectivity
    print("Step 3: Testing AWS connectivity...")
    if not check_aws_connectivity():
        return
    print()
    
    # Check if audio file exists
    print("Step 4: Checking for temp_audio.webm...")
    audio_file = Path(__file__).parent / 'temp_audio.webm'
    
    if not audio_file.exists():
        print(f"✗ Audio file not found: {audio_file}")
        print("  Expected location: BackEnd/temp_audio.webm")
        return
    
    file_size_kb = audio_file.stat().st_size / 1024
    print(f"✓ Found audio file: {audio_file.name} ({file_size_kb:.2f} KB)")
    print()
    
    # Upload file
    print("Step 5: Uploading to S3...")
    print(f"  Bucket: {os.environ.get('S3_BUCKET_NAME')}")
    print(f"  Region: {os.environ.get('AWS_REGION')}")
    print()
    
    result = upload_audio_to_s3(str(audio_file))
    
    print()
    print("=" * 70)
    print("Upload Result:")
    print("=" * 70)
    
    if result['success']:
        print(f"✓ SUCCESS!")
        print(f"  Bucket: {result['bucket']}")
        print(f"  Key: {result['key']}")
        print(f"  Size: {result['file_size']} bytes")
        print(f"  URL: {result['url']}")
    else:
        print(f"✗ FAILED!")
        print(f"  Error: {result['error']}")
    
    print()


if __name__ == '__main__':
    test_upload()


