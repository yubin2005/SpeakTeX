"""
Test Lambda Function Invocation
Tests ability to invoke Lambda function (may not exist yet)
"""

import boto3
from botocore.exceptions import ClientError
import json
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
LAMBDA_FUNCTION_NAME = "speaktex-audio-processor"

# Validate that credentials are loaded
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError(
        "AWS credentials not found. Please ensure .env file exists in backend/ directory with:\n"
        "  AWS_ACCESS_KEY_ID=your_key\n"
        "  AWS_SECRET_ACCESS_KEY=your_secret"
    )


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Testing Lambda Invocation...")
    print("="*60 + "\n")
    
    print(f"Function: {LAMBDA_FUNCTION_NAME}\n")
    
    # Initialize Lambda client
    lambda_client = boto3.client(
        'lambda',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    # Create mock S3 event payload
    mock_event = {
        "Records": [
            {
                "s3": {
                    "bucket": {
                        "name": "speaktex-audio-storage"
                    },
                    "object": {
                        "key": "test/dummy.webm"
                    }
                }
            }
        ]
    }
    
    print("Mock S3 Event:")
    print(json.dumps(mock_event, indent=2))
    print()
    
    try:
        # Try to invoke Lambda function
        print("Attempting Lambda invocation... ", end="", flush=True)
        
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(mock_event)
        )
        
        print("✅")
        
        # Parse response
        status_code = response['StatusCode']
        print(f"\nResponse Status: {status_code}")
        
        # Read payload
        payload = response['Payload'].read()
        
        if payload:
            payload_json = json.loads(payload)
            print("\nLambda Response:")
            print(json.dumps(payload_json, indent=2))
        
        # Check if invocation was successful
        if status_code == 200:
            print("\n" + "="*60)
            print("✅ Lambda invoked successfully!")
            print("="*60 + "\n")
            return True
        else:
            print("\n" + "="*60)
            print(f"⚠️  Lambda invoked but returned status {status_code}")
            print("="*60 + "\n")
            return False
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        
        if error_code == 'ResourceNotFoundException':
            print("⚠️\n")
            print(f"❌ Lambda function not found (this is OK, we'll create it later)")
            print("   But we have permission to invoke Lambda functions ✅")
            print("\n" + "="*60)
            print("✅ Lambda invocation permission confirmed")
            print("   (Function doesn't exist yet)")
            print("="*60 + "\n")
            return True  # We have permissions, just no function yet
            
        elif error_code == 'AccessDeniedException':
            print("❌\n")
            print(f"Access Denied: {e.response['Error']['Message']}")
            print("   Check IAM permissions for Lambda invocation")
            print("\n" + "="*60)
            print("❌ No Lambda invocation permission")
            print("="*60 + "\n")
            return False
            
        else:
            print("❌\n")
            print(f"Error: {e.response['Error']['Message']}")
            print("\n" + "="*60)
            print(f"❌ Lambda invocation failed: {error_code}")
            print("="*60 + "\n")
            return False
            
    except Exception as e:
        print("❌\n")
        print(f"Unexpected error: {str(e)}")
        print("\n" + "="*60)
        print("❌ Lambda test failed")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

