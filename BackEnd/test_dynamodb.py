"""
Test DynamoDB Connection and Operations
Purpose: Verify DynamoDB connectivity and table operations
"""

import os
import sys
import uuid
import time
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
                
            return True, records
        else:
            print(f"✗ Failed to read records: {result.get('error', 'Unknown error')}")
            return False, []
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False, []


def test_delete_record():
    """Test deleting a record from DynamoDB"""
    print("\n=== Testing DynamoDB Delete Operation ===")
    
    try:
        # Create DynamoDB service
        dynamodb_service = DynamoDBService()
        
        # First get records to find one to delete
        read_ok, records = test_read_records()
        
        if not read_ok or not records:
            print("✗ No records available to delete. Create a record first.")
            return False
        
        # Get the first record
        record = records[0]
        user_id = record['user_id']
        timestamp = record['timestamp']
        
        print(f"\nDeleting record:")
        print(f"  User ID: {user_id}")
        print(f"  Timestamp: {timestamp}")
        
        # Delete record
        result = dynamodb_service.delete_history_record(user_id, timestamp)
        
        if result['success']:
            print(f"✓ Successfully deleted record from DynamoDB")
            print(f"  Deleted record ID: {result['deleted_record']['id']}")
            return True
        else:
            print(f"✗ Failed to delete record: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_delete_all_records():
    """Test deleting all records for a user from DynamoDB"""
    print("\n=== Testing DynamoDB Batch Delete Operation ===")
    
    try:
        # Create DynamoDB service
        dynamodb_service = DynamoDBService()
        
        # Create a test user ID
        user_id = f"test_batch_delete_{int(time.time())}"
        
        # Create some test records
        print(f"Creating test records for user: {user_id}")
        for i in range(3):
            transcript = f"Test transcript {i+1}"
            latex = f"Test LaTeX {i+1}"
            result = dynamodb_service.save_history_record(user_id, transcript, latex)
            if result['success']:
                print(f"  ✓ Created test record {i+1}")
            else:
                print(f"  ✗ Failed to create test record {i+1}")
        
        # Verify records were created
        read_result = dynamodb_service.get_user_history(user_id)
        if not read_result['success'] or not read_result['records']:
            print("✗ Failed to create test records or retrieve them.")
            return False
        
        records_count = len(read_result['records'])
        print(f"Created {records_count} test records for user: {user_id}")
        
        # Delete all records for the test user
        print(f"\nDeleting all records for user: {user_id}")
        result = dynamodb_service.delete_all_user_history(user_id)
        
        if result['success']:
            print(f"✓ Successfully deleted all records")
            print(f"  Deleted: {result['deleted_count']}")
            print(f"  Failed: {result['failed_count']}")
            print(f"  Total: {result['total_count']}")
            
            # Verify records were deleted
            verify_result = dynamodb_service.get_user_history(user_id)
            if verify_result['success'] and len(verify_result['records']) == 0:
                print(f"✓ Verified all records were deleted")
                return True
            else:
                print(f"✗ Some records were not deleted. Remaining: {len(verify_result.get('records', []))}")
                return False
        else:
            print(f"✗ Failed to delete all records: {result.get('error', 'Unknown error')}")
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
        read_ok, _ = test_read_records()
        
        # Test delete operation
        delete_ok = False
        if read_ok:
            delete_ok = test_delete_record()
            
        # Test batch delete operation
        batch_delete_ok = test_delete_all_records()
        
        print("\n=== Summary ===")
        print(f"Connection Test: {'✓ Passed' if connection_ok else '✗ Failed'}")
        print(f"Write Test: {'✓ Passed' if write_ok else '✗ Failed'}")
        print(f"Read Test: {'✓ Passed' if read_ok else '✗ Failed'}")
        print(f"Delete Test: {'✓ Passed' if delete_ok else '✗ Failed'}")
        print(f"Batch Delete Test: {'✓ Passed' if batch_delete_ok else '✗ Failed'}")
        
        if connection_ok and write_ok and read_ok and delete_ok and batch_delete_ok:
            print("\n✓ All tests passed! DynamoDB is working correctly.")
        else:
            print("\n✗ Some tests failed. Please check the errors above.")
    else:
        print("\n✗ Connection test failed. Cannot proceed with other tests.")
