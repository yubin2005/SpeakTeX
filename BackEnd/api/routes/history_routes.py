"""
History API Routes
Purpose: Endpoints for managing SpeakTeX history records
"""

import json
from http.server import BaseHTTPRequestHandler
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Add parent directory to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Import services
from api.services.dynamodb_service import DynamoDBService


class HistoryRoutes:
    """Handler for history-related API routes"""
    
    @staticmethod
    def handle_request(handler: BaseHTTPRequestHandler) -> bool:
        """
        Process history-related requests
        
        Args:
            handler: The HTTP request handler instance
            
        Returns:
            True if request was handled, False otherwise
        """
        path = handler.path
        method = handler.command
        
        # Parse URL path
        parsed_url = urlparse(path)
        path_parts = parsed_url.path.strip('/').split('/')
        
        # Check if this is a history route
        if len(path_parts) < 2 or path_parts[0] != 'api' or path_parts[1] != 'history':
            return False
        
        # Initialize DynamoDB service
        dynamodb_service = DynamoDBService()
        
        # Route: POST /api/history
        if method == 'POST' and len(path_parts) == 2:
            return HistoryRoutes._handle_save_history(handler, dynamodb_service)
            
        # Route: GET /api/history/<user_id>
        elif method == 'GET' and len(path_parts) == 3:
            user_id = path_parts[2]
            return HistoryRoutes._handle_get_user_history(handler, dynamodb_service, user_id)
            
        # Route: DELETE /api/history/<user_id>/<timestamp>
        elif method == 'DELETE' and len(path_parts) == 4:
            user_id = path_parts[2]
            timestamp = path_parts[3]
            return HistoryRoutes._handle_delete_history(handler, dynamodb_service, user_id, timestamp)
            
        # Handle OPTIONS for CORS
        elif method == 'OPTIONS':
            HistoryRoutes._send_cors_headers(handler)
            handler.send_response(200)
            handler.end_headers()
            return True
            
        # Unknown route
        return False
    
    @staticmethod
    def _handle_save_history(handler: BaseHTTPRequestHandler, dynamodb_service: DynamoDBService) -> bool:
        """Handle POST /api/history to save a new history record"""
        try:
            # Read request body
            content_length = int(handler.headers.get('Content-Length', 0))
            body = handler.rfile.read(content_length) if content_length > 0 else b'{}'
            data = json.loads(body.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['user_id', 'transcript', 'latex']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                HistoryRoutes._send_error(handler, 400, f"Missing required fields: {', '.join(missing_fields)}")
                return True
            
            # Save history record
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
        """Handle GET /api/history/<user_id> to retrieve user history records"""
        try:
            # Parse query parameters
            parsed_url = urlparse(handler.path)
            query_params = parse_qs(parsed_url.query)
            
            # Extract limit parameter if present
            limit = None
            if 'limit' in query_params and query_params['limit']:
                try:
                    limit = int(query_params['limit'][0])
                except ValueError:
                    pass
            
            # Get user history
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
        """Handle DELETE /api/history/<user_id>/<timestamp> to delete a specific record"""
        try:
            # Delete history record
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
    def _send_json(handler: BaseHTTPRequestHandler, status_code: int, data: dict):
        """Send JSON response with CORS headers"""
        handler.send_response(status_code)
        handler.send_header('Content-Type', 'application/json')
        HistoryRoutes._send_cors_headers(handler)
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode('utf-8'))
    
    @staticmethod
    def _send_error(handler: BaseHTTPRequestHandler, status_code: int, message: str):
        """Send error response with CORS headers"""
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
        """Add CORS headers to response"""
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
