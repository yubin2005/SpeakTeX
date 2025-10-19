"""
Download Latest Audio from S3
Purpose: Downloads the most recently uploaded audio file from S3 to local BackEnd/temp_audio.webm
NOT a server - just a one-time script to pull the file down
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from api.services.s3_service import S3Service
from datetime import datetime

# Load environment variables
load_dotenv()


def download_audio_from_s3(file_key: str = None, output_path: str = None):
    """
    Download audio file from S3 to local filesystem
    
    Args:
        file_key: S3 object key to download (if None, will try to find latest)
        output_path: Local path to save file (defaults to BackEnd/temp_audio.webm)
    """
    # Get AWS credentials
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-2')
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    
    if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
        raise ValueError(
            "Missing AWS credentials. Check .env file for AWS_ACCESS_KEY_ID, "
            "AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME"
        )
    
    # Initialize S3 service
    s3_service = S3Service(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
        bucket_name=bucket_name
    )
    
    # If no file_key provided, list objects and get the latest
    if not file_key:
        print("Finding latest audio file in S3...")
        response = s3_service.s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='audio/recordings/'
        )
        
        if 'Contents' not in response or len(response['Contents']) == 0:
            raise FileNotFoundError("No audio files found in S3 bucket")
        
        # Sort by LastModified and get the most recent
        objects = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
        file_key = objects[0]['Key']
        print(f"Latest file: {file_key} (uploaded {objects[0]['LastModified']})")
    
    # Download file
    print(f"Downloading s3://{bucket_name}/{file_key}...")
    file_data = s3_service.download_file(file_key)
    
    # Determine output path
    if not output_path:
        backend_dir = Path(__file__).parent
        output_path = backend_dir / 'temp_audio.webm'
    
    # Save to local file
    with open(output_path, 'wb') as f:
        f.write(file_data)
    
    file_size_kb = len(file_data) / 1024
    print(f"✓ Downloaded successfully: {output_path}")
    print(f"  File size: {file_size_kb:.2f} KB")
    
    return str(output_path)


if __name__ == '__main__':
    """
    Run this script to download the latest audio from S3
    Usage: python download_from_s3.py
    """
    import sys
    
    print("=" * 60)
    print("Download Audio from S3")
    print("=" * 60)
    
    try:
        # Check for optional file_key argument
        file_key = sys.argv[1] if len(sys.argv) > 1 else None
        
        if file_key:
            print(f"Downloading specific file: {file_key}")
        else:
            print("Will download the most recent audio file")
        
        print()
        
        output_path = download_audio_from_s3(file_key)
        
        print("\n" + "=" * 60)
        print("SUCCESS")
        print("=" * 60)
        print(f"Audio saved to: {output_path}")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(f"Failed to download: {str(e)}")
        sys.exit(1)

