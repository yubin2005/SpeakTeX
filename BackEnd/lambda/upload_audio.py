"""
Lambda Function: Upload Audio to S3
Purpose: Upload audio file from local filesystem to S3 bucket
Trigger: Manual invocation or event-driven
Output: S3 object key and URL
"""

import os
import json
import boto3
from datetime import datetime
from pathlib import Path
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_s3_client():
    """
    Create S3 client using credentials from environment variables
    
    Returns:
        boto3 S3 client
        
    Raises:
        ValueError: If required environment variables are missing
    """
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_region = os.environ.get('AWS_REGION', 'us-east-2')
    
    if not aws_access_key_id or not aws_secret_access_key:
        raise ValueError(
            "Missing AWS credentials. Please set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY in your .env file"
        )
    
    return boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region
    )


def upload_audio_to_s3(
    file_path: str,
    bucket_name: str = None,
    custom_key: str = None
) -> dict:
    """
    Upload audio file to S3 bucket
    
    Args:
        file_path: Path to the audio file to upload
        bucket_name: S3 bucket name (defaults to env variable)
        custom_key: Custom S3 key (defaults to auto-generated with timestamp)
        
    Returns:
        Dictionary containing:
            - success: Boolean indicating success
            - bucket: S3 bucket name
            - key: S3 object key
            - url: S3 object URL
            - error: Error message if failed
            
    Raises:
        FileNotFoundError: If audio file doesn't exist
        ClientError: If S3 upload fails
    """
    # Validate file exists
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    # Get bucket name from parameter or environment
    if not bucket_name:
        bucket_name = os.environ.get('S3_BUCKET_NAME')
        if not bucket_name:
            raise ValueError(
                "S3_BUCKET_NAME not provided and not found in environment variables"
            )
    
    # Generate S3 key with timestamp
    if not custom_key:
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = file_path.name
        custom_key = f"audio/{timestamp}_{filename}"
    
    try:
        # Create S3 client
        s3_client = get_s3_client()
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Upload to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=custom_key,
            Body=file_data,
            ContentType='audio/webm'
        )
        
        # Generate S3 URL
        region = os.environ.get('AWS_REGION', 'us-east-2')
        s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{custom_key}"
        
        print(f"✓ Upload successful: s3://{bucket_name}/{custom_key}")
        
        return {
            'success': True,
            'bucket': bucket_name,
            'key': custom_key,
            'url': s3_url,
            'file_size': len(file_data)
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"✗ S3 upload failed [{error_code}]: {error_message}")
        
        return {
            'success': False,
            'error': f"S3 Error [{error_code}]: {error_message}"
        }
        
    except Exception as e:
        print(f"✗ Upload failed: {str(e)}")
        
        return {
            'success': False,
            'error': str(e)
        }


def lambda_handler(event: dict, context=None) -> dict:
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event containing:
            - file_path: Path to audio file (for local testing)
            - bucket_name: Optional S3 bucket name
            - custom_key: Optional custom S3 key
        context: Lambda context object
        
    Returns:
        Response dictionary with statusCode and body
    """
    try:
        # Extract parameters from event
        file_path = event.get('file_path', 'temp_audio.webm')
        bucket_name = event.get('bucket_name')
        custom_key = event.get('custom_key')
        
        print(f"Starting upload for: {file_path}")
        
        # Upload file
        result = upload_audio_to_s3(
            file_path=file_path,
            bucket_name=bucket_name,
            custom_key=custom_key
        )
        
        if result['success']:
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps(result)
            }
            
    except FileNotFoundError as e:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'success': False,
                'error': f"File not found: {str(e)}"
            })
        }
        
    except ValueError as e:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'error': f"Configuration error: {str(e)}"
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            })
        }


if __name__ == '__main__':
    """
    Local testing entry point
    Run this script directly to test upload functionality
    """
    # Test event for local execution
    test_event = {
        'file_path': 'temp_audio.webm'
    }
    
    print("=" * 60)
    print("Testing S3 Upload Lambda Function")
    print("=" * 60)
    
    response = lambda_handler(test_event)
    
    print("\nResponse:")
    print(json.dumps(json.loads(response['body']), indent=2))
    print(f"\nStatus Code: {response['statusCode']}")

