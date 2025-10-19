"""
S3 Service
Purpose: Handle all S3 operations including uploads, downloads, and presigned URLs
Abstracts boto3 S3 operations with error handling and logging
"""

import boto3
from botocore.exceptions import ClientError, BotoCoreError
import logging
from typing import Dict, Optional
from .aws_config import get_s3_client

logger = logging.getLogger(__name__)


class S3Service:
    """
    Service class for S3 operations
    Handles file uploads, downloads, presigned URL generation, and file existence checks
    """
    
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        region_name: str,
        bucket_name: str
    ):
        """
        Initialize S3 service with AWS credentials
        
        Args:
            aws_access_key_id: AWS access key ID
            aws_secret_access_key: AWS secret access key
            region_name: AWS region name
            bucket_name: S3 bucket name for storage
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        
        # Create S3 client
        self.s3_client = get_s3_client(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name
        )
        
        logger.info(f"S3Service initialized for bucket: {bucket_name}")
    
    
    def upload_file(
        self,
        file_data: bytes,
        file_key: str,
        content_type: str = 'audio/webm'
    ) -> Dict[str, str]:
        """
        Upload file to S3 bucket
        
        Args:
            file_data: File content as bytes
            file_key: S3 object key (path in bucket)
            content_type: MIME type of file
            
        Returns:
            Dictionary with upload information
            
        Raises:
            ClientError: If upload fails
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=content_type
            )
            
            logger.info(f"File uploaded successfully: s3://{self.bucket_name}/{file_key}")
            
            return {
                'bucket': self.bucket_name,
                'key': file_key,
                'url': f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_key}"
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"S3 upload failed [{error_code}]: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            raise
    
    
    def download_file(self, file_key: str) -> bytes:
        """
        Download file from S3 bucket
        
        Args:
            file_key: S3 object key to download
            
        Returns:
            File content as bytes
            
        Raises:
            ClientError: If download fails or file doesn't exist
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            file_data = response['Body'].read()
            
            logger.info(f"File downloaded successfully: s3://{self.bucket_name}/{file_key}")
            return file_data
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'NoSuchKey':
                logger.warning(f"File not found: {file_key}")
            else:
                logger.error(f"S3 download failed [{error_code}]: {str(e)}")
            
            raise
        except Exception as e:
            logger.error(f"Unexpected error during S3 download: {str(e)}")
            raise
    
    
    def file_exists(self, file_key: str) -> bool:
        """
        Check if file exists in S3 bucket
        
        Args:
            file_key: S3 object key to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == '404':
                return False
            else:
                logger.error(f"Error checking file existence [{error_code}]: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error checking file existence: {str(e)}")
            raise
    
    
    def generate_presigned_upload_url(
        self,
        file_key: str,
        content_type: str = 'audio/webm',
        expires_in: int = 300
    ) -> Dict[str, str]:
        """
        Generate presigned URL for direct upload from client
        
        Args:
            file_key: S3 object key for upload destination
            content_type: MIME type of file to be uploaded
            expires_in: URL expiration time in seconds (default: 5 minutes)
            
        Returns:
            Dictionary with presigned URL and fields
            
        Raises:
            ClientError: If URL generation fails
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key,
                    'ContentType': content_type
                },
                ExpiresIn=expires_in,
                HttpMethod='PUT'
            )
            
            logger.info(f"Presigned upload URL generated for: {file_key} (expires in {expires_in}s)")
            
            return {
                'url': presigned_url,
                'method': 'PUT',
                'headers': {
                    'Content-Type': content_type
                }
            }
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {str(e)}")
            raise
    
    
    def generate_presigned_download_url(
        self,
        file_key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate presigned URL for downloading file
        
        Args:
            file_key: S3 object key to download
            expires_in: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned download URL as string
            
        Raises:
            ClientError: If URL generation fails
        """
        try:
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expires_in
            )
            
            logger.info(f"Presigned download URL generated for: {file_key}")
            return presigned_url
            
        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating presigned download URL: {str(e)}")
            raise
    
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from S3 bucket
        
        Args:
            file_key: S3 object key to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            ClientError: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            logger.info(f"File deleted successfully: s3://{self.bucket_name}/{file_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error deleting file: {str(e)}")
            raise

