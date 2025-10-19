"""
End-to-End Test: Recording Flow
Tests the complete flow: Generate upload URL → Upload to S3 → Download from S3
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from lambda.get_upload_url import generate_upload_url
from api.services.s3_service import S3Service

# Load environment variables
load_dotenv()


def test_complete_flow():
    """
    Test the complete recording flow:
    1. Generate presigned upload URL
    2. Simulate upload to S3
    3. Download from S3 to temp_audio.webm
    """
    print("=" * 60)
    print("End-to-End Recording Flow Test")
    print("=" * 60)
    
    # Step 1: Generate upload URL
    print("\n[1/3] Generating presigned upload URL...")
    try:
        upload_data = generate_upload_url('webm')
        print(f"✓ Upload URL generated")
        print(f"  File key: {upload_data['file_key']}")
        print(f"  Expires in: {upload_data['expires_in']} seconds")
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False
    
    # Step 2: Simulate file upload (we'll create a test audio file)
    print("\n[2/3] Creating test audio file and uploading to S3...")
    try:
        # Create a small test webm file (just some bytes)
        test_audio_data = b'WEBM test data - this would be actual audio in production'
        
        # Initialize S3 service
        s3_service = S3Service(
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'us-east-2'),
            bucket_name=os.environ.get('S3_BUCKET_NAME')
        )
        
        # Upload directly using S3 service (simulating what frontend will do)
        result = s3_service.upload_file(
            file_data=test_audio_data,
            file_key=upload_data['file_key'],
            content_type='audio/webm'
        )
        
        print(f"✓ Test file uploaded to S3")
        print(f"  Bucket: {result['bucket']}")
        print(f"  Key: {result['key']}")
        
    except Exception as e:
        print(f"✗ Upload failed: {str(e)}")
        return False
    
    # Step 3: Download from S3
    print("\n[3/3] Downloading from S3 to BackEnd/temp_audio.webm...")
    try:
        file_data = s3_service.download_file(upload_data['file_key'])
        
        # Save to temp_audio.webm
        backend_dir = Path(__file__).parent
        output_path = backend_dir / 'temp_audio.webm'
        
        with open(output_path, 'wb') as f:
            f.write(file_data)
        
        file_size = len(file_data)
        print(f"✓ Downloaded successfully")
        print(f"  Saved to: {output_path}")
        print(f"  File size: {file_size} bytes")
        
    except Exception as e:
        print(f"✗ Download failed: {str(e)}")
        return False
    
    # Verify file exists
    if output_path.exists():
        print("\n" + "=" * 60)
        print("SUCCESS")
        print("=" * 60)
        print(f"✓ Complete flow test passed!")
        print(f"✓ File verified: {output_path}")
        return True
    else:
        print("\n✗ File not found after download")
        return False


def verify_environment():
    """Verify all required environment variables are set"""
    print("\nVerifying environment configuration...")
    
    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'S3_BUCKET_NAME'
    ]
    
    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
            print(f"  ✗ {var} - NOT SET")
        else:
            print(f"  ✓ {var} - OK")
    
    if missing:
        print(f"\n✗ Missing environment variables: {', '.join(missing)}")
        print("  Please check your .env file")
        return False
    
    print("\n✓ All environment variables set")
    return True


if __name__ == '__main__':
    print("\nPre-flight checks...")
    
    if not verify_environment():
        print("\n" + "=" * 60)
        print("FAILED - Environment not configured")
        print("=" * 60)
        sys.exit(1)
    
    print()
    
    success = test_complete_flow()
    
    if not success:
        print("\n" + "=" * 60)
        print("FAILED")
        print("=" * 60)
        sys.exit(1)

