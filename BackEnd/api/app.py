"""
SpeakTeX API - Main Application
Purpose: Flask API server for handling audio uploads and result retrieval
Architecture: RESTful API with S3 integration for serverless audio processing
"""

from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
import logging

# Import route blueprints
from routes.upload import upload_bp
from routes.results import results_bp


def create_app():
    """
    Application factory pattern for Flask app creation
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Validate configuration
    try:
        config.validate_config()
    except ValueError as e:
        logging.error(f"Configuration error: {e}")
        raise
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGIN'],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if app.config['DEBUG'] else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Register blueprints
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(results_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint for monitoring
        Returns service status and configuration info
        """
        return jsonify({
            'status': 'healthy',
            'service': 'speaktex-api',
            'version': '1.0.0',
            'config': {
                'debug': app.config['DEBUG'],
                'max_audio_size_mb': app.config['MAX_AUDIO_SIZE_MB'],
                's3_bucket': app.config['S3_BUCKET_NAME']
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'success': False,
            'error': 'Bad request',
            'message': str(error)
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'message': str(error)
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        logging.error(f"Internal error: {error}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again.'
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable errors (rate limits)"""
        return jsonify({
            'success': False,
            'error': 'Service temporarily unavailable',
            'message': 'Too many requests. Please wait 10 seconds and try again.'
        }), 503
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )

