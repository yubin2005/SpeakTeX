"""
Test DynamoDB Connection and Operations
Purpose: Verify DynamoDB connectivity and table operations
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Add parent directory to path
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

# Load environment variables
env_path = parent_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Import DynamoDB service
from api.services.dynamodb_service import DynamoDBService


def test_dynamodb_connection():
    """Test basic DynamoDB connection"""
    print("\n=== Testing DynamoDB Connection ===")
    
    try:
        # Get AWS credentials from environment
        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        aws_region = os.environ.get('AWS_REGION', 'us-east-2')
        table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'speaktex-history')
        
        if not aws_access_key_id or not aws_secret_access_key:
            print("✗ ERROR: Missing AWS credentials in environment variables")
            print("  Please check your .env file")
            return False
            
        print(f"AWS Region: {aws_region}")
        print(f"Table Name: {table_name}")
        
        # Create DynamoDB client
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        # Try to describe the table
        table = dynamodb.Table(table_name)
        response = table.meta.client.describe_table(TableName=table_name)
        
        print(f"✓ Successfully connected to DynamoDB")
        print(f"✓ Table '{table_name}' exists")
        
        # Print table details
        table_details = response['Table']
        print(f"  Creation Date: {table_details['CreationDateTime']}")
        print(f"  Item Count: {table_details['ItemCount']}")
        print(f"  Status: {table_details['TableStatus']}")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"✗ DynamoDB Error: [{error_code}] {error_message}")
        
        if error_code == 'ResourceNotFoundException':
            print(f"  The table '{table_name}' does not exist")
            print(f"  Please create the table with:")
            print(f"  - Partition key: user_id (String)")
            print(f"  - Sort key: timestamp (String)")
        
        return False
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_write_record():
    """Test writing a record to DynamoDB"""
    print("\n=== Testing DynamoDB Write Operation ===")
    
    try:
        # Create DynamoDB service
        dynamodb_service = DynamoDBService()
        
        # Generate test data
        user_id = "test_user"
        transcript = "x squared plus y squared equals z squared"
        latex = "x^2 + y^2 = z^2"
        
        print(f"Writing test record:")
        print(f"  User ID: {user_id}")
        print(f"  Transcript: {transcript}")
        print(f"  LaTeX: {latex}")
        
        # Save record
        result = dynamodb_service.save_history_record(user_id, transcript, latex)
        
        if result['success']:
            print(f"✓ Successfully wrote record to DynamoDB")
            print(f"  Record ID: {result['record']['id']}")
            print(f"  Timestamp: {result['record']['timestamp']}")
            return True
        else:
            print(f"✗ Failed to write record: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_read_records():
    """Test reading records from DynamoDB"""
    print("\n=== Testing DynamoDB Read Operation ===")
    
    try:
        # Create DynamoDB service
        dynamodb_service = DynamoDBService()
        
        # User ID to query
        user_id = "test_user"
        
        print(f"Reading records for user: {user_id}")
        
        # Get records
        result = dynamodb_service.get_user_history(user_id)
        
        if result['success']:
            records = result['records']
            count = result['count']
            
            print(f"✓ Successfully read {count} records from DynamoDB")
            
            for i, record in enumerate(records[:3], 1):  # Show first 3 records
                print(f"\nRecord {i}:")
                print(f"  ID: {record['id']}")
                print(f"  Timestamp: {record['timestamp']}")
                print(f"  Transcript: {record['transcript']}")
                print(f"  LaTeX: {record['latex']}")
                
            if count > 3:
                print(f"\n... and {count - 3} more records")
                
            return True
        else:
            print(f"✗ Failed to read records: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DynamoDB Test Script")
    print("=" * 60)
    
    # Test connection
    connection_ok = test_dynamodb_connection()
    
    if connection_ok:
        # Test write operation
        write_ok = test_write_record()
        
        # Test read operation
        read_ok = test_read_records()
        
        print("\n=== Summary ===")
        print(f"Connection Test: {'✓ Passed' if connection_ok else '✗ Failed'}")
        print(f"Write Test: {'✓ Passed' if write_ok else '✗ Failed'}")
        print(f"Read Test: {'✓ Passed' if read_ok else '✗ Failed'}")
        
        if connection_ok and write_ok and read_ok:
            print("\n✓ All tests passed! DynamoDB is working correctly.")
        else:
            print("\n✗ Some tests failed. Please check the errors above.")
    else:
        print("\n✗ Connection test failed. Cannot proceed with other tests.")
