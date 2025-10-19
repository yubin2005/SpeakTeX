"""
Lambda Function: Generate Presigned S3 Upload URL
Purpose: Provides frontend with a presigned URL to upload audio directly to S3
No audio data passes through this function - just URL generation
"""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from api.services.s3_service import S3Service

# Load environment variables from BackEnd/.env
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)


def generate_upload_url(file_extension: str = 'webm') -> dict:
    """
    Generate presigned S3 upload URL
    
    Args:
        file_extension: File extension for the audio file
        
    Returns:
        Dictionary with presigned URL and upload details
        
    Raises:
        ValueError: If AWS credentials are missing
    """
    # Get AWS credentials from environment
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-2')
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    
    if not all([aws_access_key_id, aws_secret_access_key, bucket_name]):
        raise ValueError(
            "Missing required AWS configuration. Check AWS_ACCESS_KEY_ID, "
            "AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME in .env file"
        )
    
    # Initialize S3 service
    s3_service = S3Service(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
        bucket_name=bucket_name
    )
    
    # Generate unique file key with timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    file_key = f"audio/recordings/{timestamp}.{file_extension}"
    
    # Generate presigned upload URL (5 minutes expiration)
    presigned_data = s3_service.generate_presigned_upload_url(
        file_key=file_key,
        content_type='audio/webm',
        expires_in=300
    )
    
    return {
        'success': True,
        'upload_url': presigned_data['url'],
        'file_key': file_key,
        'bucket': bucket_name,
        'method': presigned_data['method'],
        'headers': presigned_data['headers'],
        'expires_in': 300
    }


def lambda_handler(event: dict, context=None) -> dict:
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event (can be empty or contain file_extension)
        context: Lambda context object
        
    Returns:
        Response dictionary with statusCode and body
    """
    try:
        # Extract file extension if provided
        file_extension = event.get('file_extension', 'webm')
        
        print(f"Generating presigned upload URL for .{file_extension} file")
        
        # Generate upload URL
        result = generate_upload_url(file_extension)
        
        print(f"✓ Presigned URL generated: {result['file_key']}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
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
                'error': f"Configuration error: {str(e)}"
            })
        }
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f"Failed to generate upload URL: {str(e)}"
            })
        }


if __name__ == '__main__':
    """
    Local testing entry point
    """
    print("=" * 60)
    print("Testing Presigned Upload URL Generation")
    print("=" * 60)
    
    test_event = {
        'file_extension': 'webm'
    }
    
    response = lambda_handler(test_event)
    
    print("\nResponse:")
    body = json.loads(response['body'])
    print(json.dumps(body, indent=2))
    print(f"\nStatus Code: {response['statusCode']}")
    
    if body.get('success'):
        print(f"\n✓ Upload URL generated successfully")
        print(f"  File will be saved as: {body['file_key']}")
        print(f"  Expires in: {body['expires_in']} seconds")

