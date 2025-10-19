"""
AWS Connection Test Script
Purpose: Verify AWS credentials and service connectivity
Run this script to test your AWS configuration before deploying

Usage:
    python test_aws_connection.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from services.aws_config import test_aws_connectivity
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """
    Main test function
    Tests AWS credentials and connectivity to required services
    """
    print("\n" + "="*60)
    print("AWS Connection Test - SpeakTeX Backend")
    print("="*60 + "\n")
    
    # Validate configuration
    try:
        Config.validate_config()
        print("✓ Configuration loaded successfully\n")
    except ValueError as e:
        print(f"✗ Configuration error: {e}\n")
        print("Please ensure your .env file is properly configured.")
        return False
    
    # Display configuration (sanitized)
    print("Configuration:")
    print(f"  AWS Region: {Config.AWS_REGION}")
    print(f"  S3 Bucket: {Config.S3_BUCKET_NAME}")
    print(f"  Access Key: {Config.AWS_ACCESS_KEY_ID[:8]}...")
    print(f"  Max Audio Size: {Config.MAX_AUDIO_SIZE_MB}MB")
    print()
    
    # Run connectivity tests
    print("Running connectivity tests...\n")
    
    results = test_aws_connectivity(
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION,
        bucket_name=Config.S3_BUCKET_NAME
    )
    
    # Display results
    print("\nTest Results:")
    print("-" * 60)
    print(f"  Credentials Valid:    {'✓ PASS' if results['credentials'] else '✗ FAIL'}")
    print(f"  S3 Access:            {'✓ PASS' if results['s3'] else '✗ FAIL'}")
    print(f"  Transcribe Access:    {'✓ PASS' if results['transcribe'] else '✗ FAIL'}")
    print(f"  Bucket Access:        {'✓ PASS' if results['bucket_access'] else '✗ FAIL'}")
    print("-" * 60)
    
    # Display errors if any
    if results['errors']:
        print("\nErrors encountered:")
        for error in results['errors']:
            print(f"  • {error}")
    
    # Overall result
    print()
    all_passed = all([
        results['credentials'],
        results['s3'],
        results['transcribe'],
        results['bucket_access']
    ])
    
    if all_passed:
        print("="*60)
        print("✓ All tests passed! AWS configuration is working correctly.")
        print("="*60)
        return True
    else:
        print("="*60)
        print("✗ Some tests failed. Please check your AWS configuration.")
        print("="*60)
        print("\nTroubleshooting tips:")
        print("  1. Verify AWS credentials in .env file")
        print("  2. Check IAM permissions for your AWS user")
        print("  3. Ensure S3 bucket exists and is accessible")
        print("  4. Verify AWS region is correct")
        print("  5. Check internet connectivity")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

