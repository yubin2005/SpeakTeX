import os
import uuid
import json
import boto3
from datetime import datetime
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Any

import sys
from pathlib import Path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from api.config import Config, get_config


class DynamoDBService:
    
    def __init__(self):
        config = get_config()
        
        self.table_name = config.DYNAMODB_TABLE_NAME
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_REGION
        )
        self.table = self.dynamodb.Table(self.table_name)
    
    def save_history_record(self, user_id: str, transcript: str, latex: str) -> Dict[str, Any]:
        timestamp = datetime.utcnow().isoformat()
        record_id = str(uuid.uuid4())
        
        item = {
            'user_id': user_id,
            'timestamp': timestamp,
            'id': record_id,
            'transcript': transcript,
            'latex': latex
        }
        
        try:
            self.table.put_item(Item=item)
            return {
                'success': True,
                'record': item
            }
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"DynamoDB Error: [{error_code}] {error_message}")
            
            return {
                'success': False,
                'error': f"Failed to save history record: {error_message}"
            }
    
    def get_user_history(self, user_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        try:
            query_params = {
                'KeyConditionExpression': boto3.dynamodb.conditions.Key('user_id').eq(user_id),
                'ScanIndexForward': False
            }
            
            if limit and isinstance(limit, int) and limit > 0:
                query_params['Limit'] = limit
            
            response = self.table.query(**query_params)
            
            return {
                'success': True,
                'records': response.get('Items', []),
                'count': len(response.get('Items', [])),
                'last_evaluated_key': response.get('LastEvaluatedKey')
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"DynamoDB Error: [{error_code}] {error_message}")
            
            return {
                'success': False,
                'error': f"Failed to get user history: {error_message}"
            }
    
    def delete_history_record(self, user_id: str, timestamp: str) -> Dict[str, Any]:
        try:
            response = self.table.delete_item(
                Key={
                    'user_id': user_id,
                    'timestamp': timestamp
                },
                ReturnValues='ALL_OLD'
            )
            
            deleted_item = response.get('Attributes')
            if not deleted_item:
                return {
                    'success': False,
                    'error': 'Record not found'
                }
            
            return {
                'success': True,
                'deleted_record': deleted_item
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"DynamoDB Error: [{error_code}] {error_message}")
            
            return {
                'success': False,
                'error': f"Failed to delete history record: {error_message}"
            }
            
    def delete_all_user_history(self, user_id: str) -> Dict[str, Any]:
        try:
            result = self.get_user_history(user_id)
            
            if not result['success']:
                return result
                
            records = result['records']
            
            if not records:
                return {
                    'success': True,
                    'message': 'No records found to delete',
                    'deleted_count': 0
                }
            
            deleted_count = 0
            failed_count = 0
            
            for record in records:
                timestamp = record['timestamp']
                delete_result = self.delete_history_record(user_id, timestamp)
                
                if delete_result['success']:
                    deleted_count += 1
                else:
                    failed_count += 1
            
            return {
                'success': True,
                'deleted_count': deleted_count,
                'failed_count': failed_count,
                'total_count': len(records)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to delete user history: {str(e)}"
            }
