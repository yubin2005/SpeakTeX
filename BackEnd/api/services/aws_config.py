"""
AWS Configuration Service
Purpose: Centralized AWS SDK configuration and session management
Provides reusable boto3 session and client factories
"""

import boto3
from botocore.config import Config as BotoConfig
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def get_aws_session(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-2'
) -> boto3.Session:
    """
    Create and configure AWS boto3 session
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        
    Returns:
        Configured boto3 Session object
    """
    try:
        session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        logger.debug(f"AWS session created for region: {region_name}")
        return session
        
    except Exception as e:
        logger.error(f"Failed to create AWS session: {str(e)}")
        raise


def get_s3_client(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-2',
    signature_version: str = 's3v4'
):
    """
    Create configured S3 client with custom settings
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        signature_version: S3 signature version (default: s3v4)
        
    Returns:
        Configured boto3 S3 client
    """
    try:
        # Custom boto configuration
        boto_config = BotoConfig(
            region_name=region_name,
            signature_version=signature_version,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            connect_timeout=5,
            read_timeout=30
        )
        
        session = get_aws_session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        s3_client = session.client('s3', config=boto_config)
        
        logger.debug("S3 client created successfully")
        return s3_client
        
    except Exception as e:
        logger.error(f"Failed to create S3 client: {str(e)}")
        raise


def get_transcribe_client(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-2'
):
    """
    Create configured AWS Transcribe client
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        
    Returns:
        Configured boto3 Transcribe client
    """
    try:
        boto_config = BotoConfig(
            region_name=region_name,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            connect_timeout=5,
            read_timeout=60  # Transcribe may take longer
        )
        
        session = get_aws_session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        transcribe_client = session.client('transcribe', config=boto_config)
        
        logger.debug("Transcribe client created successfully")
        return transcribe_client
        
    except Exception as e:
        logger.error(f"Failed to create Transcribe client: {str(e)}")
        raise


def get_dynamodb_resource(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-2'
):
    """
    Create configured DynamoDB resource (for future use)
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        
    Returns:
        Configured boto3 DynamoDB resource
    """
    try:
        session = get_aws_session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        dynamodb = session.resource('dynamodb')
        
        logger.debug("DynamoDB resource created successfully")
        return dynamodb
        
    except Exception as e:
        logger.error(f"Failed to create DynamoDB resource: {str(e)}")
        raise


def validate_aws_credentials(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-2'
) -> bool:
    """
    Validate AWS credentials by making a simple API call
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        
    Returns:
        True if credentials are valid, False otherwise
    """
    try:
        session = get_aws_session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        # Try to list S3 buckets as validation
        sts = session.client('sts')
        sts.get_caller_identity()
        
        logger.info("AWS credentials validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"AWS credentials validation failed: {str(e)}")
        return False


def test_aws_connectivity(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    region_name: str = 'us-east-2',
    bucket_name: Optional[str] = None
) -> dict:
    """
    Comprehensive test of AWS connectivity and service access
    Tests S3, Transcribe, and credential validity
    
    Args:
        aws_access_key_id: AWS access key ID
        aws_secret_access_key: AWS secret access key
        region_name: AWS region name
        bucket_name: Optional S3 bucket name to test access
        
    Returns:
        Dictionary with test results for each service
    """
    results = {
        'credentials': False,
        's3': False,
        'transcribe': False,
        'bucket_access': False,
        'errors': []
    }
    
    # Test 1: Validate credentials
    try:
        if validate_aws_credentials(aws_access_key_id, aws_secret_access_key, region_name):
            results['credentials'] = True
            logger.info("✓ Credentials valid")
    except Exception as e:
        results['errors'].append(f"Credentials test failed: {str(e)}")
        logger.error(f"✗ Credentials test failed: {str(e)}")
        return results  # No point continuing if credentials are invalid
    
    # Test 2: S3 access
    try:
        s3_client = get_s3_client(aws_access_key_id, aws_secret_access_key, region_name)
        s3_client.list_buckets()
        results['s3'] = True
        logger.info("✓ S3 access confirmed")
    except Exception as e:
        results['errors'].append(f"S3 test failed: {str(e)}")
        logger.error(f"✗ S3 test failed: {str(e)}")
    
    # Test 3: Transcribe access
    try:
        transcribe_client = get_transcribe_client(aws_access_key_id, aws_secret_access_key, region_name)
        # Just check if we can create the client and make a list call
        transcribe_client.list_transcription_jobs(MaxResults=1)
        results['transcribe'] = True
        logger.info("✓ Transcribe access confirmed")
    except Exception as e:
        results['errors'].append(f"Transcribe test failed: {str(e)}")
        logger.error(f"✗ Transcribe test failed: {str(e)}")
    
    # Test 4: Specific bucket access (if provided)
    if bucket_name:
        try:
            s3_client = get_s3_client(aws_access_key_id, aws_secret_access_key, region_name)
            s3_client.head_bucket(Bucket=bucket_name)
            results['bucket_access'] = True
            logger.info(f"✓ Bucket '{bucket_name}' access confirmed")
        except Exception as e:
            results['errors'].append(f"Bucket access test failed: {str(e)}")
            logger.error(f"✗ Bucket '{bucket_name}' access failed: {str(e)}")
    
    return results

