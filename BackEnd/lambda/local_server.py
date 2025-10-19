"""
Local Lambda Test Server
Purpose: Simple HTTP server to test Lambda functions locally
NOT for production - just for development/testing
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os

# Import from same directory
from get_upload_url import lambda_handler as get_upload_url_handler
from transcribe_audio import lambda_handler as transcribe_audio_handler


class LambdaTestHandler(BaseHTTPRequestHandler):
    """HTTP request handler that simulates Lambda function invocation"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS, GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/get-upload-url':
            self._handle_get_upload_url()
        elif self.path == '/transcribe':
            self._handle_transcribe()
        else:
            self._send_error(404, 'Endpoint not found')
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self._send_json({'status': 'ok', 'message': 'Lambda test server running'})
        else:
            self._send_error(404, 'Endpoint not found')
    
    def _handle_get_upload_url(self):
        """Handle upload URL generation request"""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            event = json.loads(body.decode('utf-8'))
            
            # Invoke Lambda handler
            response = get_upload_url_handler(event)
            
            # Send response
            self.send_response(response['statusCode'])
            for header, value in response.get('headers', {}).items():
                self.send_header(header, value)
            self.end_headers()
            
            self.wfile.write(response['body'].encode('utf-8'))
            
        except Exception as e:
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def _handle_transcribe(self):
        """Handle transcription request"""
        try:
            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            event = json.loads(body.decode('utf-8'))
            
            # Invoke Lambda handler
            response = transcribe_audio_handler(event)
            
            # Send response
            self.send_response(response['statusCode'])
            for header, value in response.get('headers', {}).items():
                self.send_header(header, value)
            self.end_headers()
            
            self.wfile.write(response['body'].encode('utf-8'))
            
        except Exception as e:
            self._send_error(500, f'Internal server error: {str(e)}')
    
    def _send_json(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, code, message):
        """Send error response"""
        self._send_json({'error': message}, code)
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=5000):
    """Run local Lambda test server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, LambdaTestHandler)
    
    print("=" * 60)
    print("Local Lambda Test Server")
    print("=" * 60)
    print(f"Server running on http://localhost:{port}")
    print("\nAvailable endpoints:")
    print(f"  POST http://localhost:{port}/get-upload-url")
    print(f"  POST http://localhost:{port}/transcribe")
    print(f"  GET  http://localhost:{port}/health")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    run_server(port)

