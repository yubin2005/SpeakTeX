import json
from http.server import BaseHTTPRequestHandler
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from api.services.dynamodb_service import DynamoDBService


class HistoryRoutes:
    
    @staticmethod
    def handle_request(handler: BaseHTTPRequestHandler) -> bool:
        path = handler.path
        method = handler.command
        
        parsed_url = urlparse(path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        if len(path_parts) < 2 or path_parts[0] != 'api' or path_parts[1] != 'history':
            return False
        
        dynamodb_service = DynamoDBService()
        
        if method == 'POST' and len(path_parts) == 2:
            return HistoryRoutes._handle_save_history(handler, dynamodb_service)
            
        elif method == 'GET' and len(path_parts) == 3:
            user_id = path_parts[2]
            return HistoryRoutes._handle_get_user_history(handler, dynamodb_service, user_id)
            
        elif method == 'DELETE' and len(path_parts) == 4:
            user_id = path_parts[2]
            timestamp = path_parts[3]
            return HistoryRoutes._handle_delete_history(handler, dynamodb_service, user_id, timestamp)
            
        elif method == 'DELETE' and len(path_parts) == 3:
            user_id = path_parts[2]
            return HistoryRoutes._handle_delete_all_history(handler, dynamodb_service, user_id)
            
        elif method == 'OPTIONS':
            handler.send_response(200)
            HistoryRoutes._send_cors_headers(handler)
            handler.end_headers()
            return True
            
        return False
    
    @staticmethod
    def _handle_save_history(handler: BaseHTTPRequestHandler, dynamodb_service: DynamoDBService) -> bool:
        try:
            content_length = int(handler.headers.get('Content-Length', 0))
            body = handler.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(body.decode('utf-8'))
            
            required_fields = ['user_id', 'transcript', 'latex']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                HistoryRoutes._send_error(handler, 400, f"Missing required fields: {', '.join(missing_fields)}")
                return True
            
            result = dynamodb_service.save_history_record(
                user_id=data['user_id'],
                transcript=data['transcript'],
                latex=data['latex']
            )
            
            if result['success']:
                HistoryRoutes._send_json(handler, 201, result)
            else:
                HistoryRoutes._send_error(handler, 500, result['error'])
                
            return True
            
        except json.JSONDecodeError:
            HistoryRoutes._send_error(handler, 400, "Invalid JSON in request body")
            return True
            
        except Exception as e:
            HistoryRoutes._send_error(handler, 500, f"Internal server error: {str(e)}")
            return True
    
    @staticmethod
    def _handle_get_user_history(handler: BaseHTTPRequestHandler, dynamodb_service: DynamoDBService, user_id: str) -> bool:
        try:
            parsed_url = urlparse(handler.path)
            query_params = parse_qs(parsed_url.query)
            
            limit = None
            if 'limit' in query_params and query_params['limit']:
                try:
                    limit = int(query_params['limit'][0])
                except ValueError:
                    pass
            
            result = dynamodb_service.get_user_history(user_id, limit)
            
            if result['success']:
                HistoryRoutes._send_json(handler, 200, result)
            else:
                HistoryRoutes._send_error(handler, 500, result['error'])
                
            return True
            
        except Exception as e:
            HistoryRoutes._send_error(handler, 500, f"Internal server error: {str(e)}")
            return True
    
    @staticmethod
    def _handle_delete_history(handler: BaseHTTPRequestHandler, dynamodb_service: DynamoDBService, user_id: str, timestamp: str) -> bool:
        try:
            result = dynamodb_service.delete_history_record(user_id, timestamp)
            
            if result['success']:
                HistoryRoutes._send_json(handler, 200, result)
            elif 'Record not found' in result.get('error', ''):
                HistoryRoutes._send_error(handler, 404, result['error'])
            else:
                HistoryRoutes._send_error(handler, 500, result['error'])
                
            return True
            
        except Exception as e:
            HistoryRoutes._send_error(handler, 500, f"Internal server error: {str(e)}")
            return True
            
    @staticmethod
    def _handle_delete_all_history(handler: BaseHTTPRequestHandler, dynamodb_service: DynamoDBService, user_id: str) -> bool:
        try:
            result = dynamodb_service.delete_all_user_history(user_id)
            
            if result['success']:
                HistoryRoutes._send_json(handler, 200, result)
            else:
                HistoryRoutes._send_error(handler, 500, result['error'])
                
            return True
            
        except Exception as e:
            HistoryRoutes._send_error(handler, 500, f"Internal server error: {str(e)}")
            return True
    
    @staticmethod
    def _send_json(handler: BaseHTTPRequestHandler, status_code: int, data: dict):
        handler.send_response(status_code)
        handler.send_header('Content-Type', 'application/json')
        HistoryRoutes._send_cors_headers(handler)
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode('utf-8'))
    
    @staticmethod
    def _send_error(handler: BaseHTTPRequestHandler, status_code: int, message: str):
        handler.send_response(status_code)
        handler.send_header('Content-Type', 'application/json')
        HistoryRoutes._send_cors_headers(handler)
        handler.end_headers()
        handler.wfile.write(json.dumps({
            'success': False,
            'error': message
        }).encode('utf-8'))
    
    @staticmethod
    def _send_cors_headers(handler: BaseHTTPRequestHandler):
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
