"""
Results Routes
Purpose: Fetch processing results from S3 after Lambda function completes
Provides polling endpoint for checking processing status
"""

from flask import Blueprint, request, jsonify, current_app
from services.s3_service import S3Service
import logging
import json

results_bp = Blueprint('results', __name__)
logger = logging.getLogger(__name__)


@results_bp.route('/results/<path:file_key>', methods=['GET'])
def get_result(file_key):
    """
    Retrieve processing result for a specific audio file
    
    URL Parameters:
        file_key: S3 key of uploaded audio file (from upload response)
    
    Response:
        {
            "success": true,
            "status": "completed|processing|failed",
            "transcript": "x squared plus y squared",
            "latex": "x^2 + y^2",
            "audio_key": "uploads/...",
            "error": null
        }
    """
    try:
        # Convert upload key to result key
        result_key = file_key.replace('uploads/', 'results/').rsplit('.', 1)[0] + '.json'
        
        logger.info(f"Fetching result for key: {result_key}")
        
        # Initialize S3 service
        s3_service = S3Service(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION'],
            bucket_name=current_app.config['S3_BUCKET_NAME']
        )
        
        # Check if result exists
        if not s3_service.file_exists(result_key):
            # Result not yet available - still processing
            return jsonify({
                'success': True,
                'status': 'processing',
                'message': 'Audio is still being processed. Please check again in a few seconds.'
            }), 202  # 202 Accepted - processing not complete
        
        # Download result from S3
        result_data = s3_service.download_file(result_key)
        result = json.loads(result_data.decode('utf-8'))
        
        logger.info(f"Successfully retrieved result for: {file_key}")
        
        return jsonify({
            'success': True,
            'status': result.get('status', 'completed'),
            'transcript': result.get('transcript'),
            'latex': result.get('latex'),
            'audio_key': result.get('audio_key'),
            'error': result.get('error')
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching result: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': 'Failed to retrieve result',
            'message': str(e)
        }), 500


@results_bp.route('/results/batch', methods=['POST'])
def get_batch_results():
    """
    Retrieve multiple results at once (for history panel)
    
    Request body:
        {
            "file_keys": ["uploads/...", "uploads/..."]
        }
    
    Response:
        {
            "success": true,
            "results": [
                {
                    "file_key": "uploads/...",
                    "status": "completed",
                    "transcript": "...",
                    "latex": "..."
                },
                ...
            ]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'file_keys' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing file_keys in request body'
            }), 400
        
        file_keys = data['file_keys']
        
        if not isinstance(file_keys, list):
            return jsonify({
                'success': False,
                'error': 'file_keys must be an array'
            }), 400
        
        # Initialize S3 service
        s3_service = S3Service(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION'],
            bucket_name=current_app.config['S3_BUCKET_NAME']
        )
        
        results = []
        
        # Fetch each result
        for file_key in file_keys:
            result_key = file_key.replace('uploads/', 'results/').rsplit('.', 1)[0] + '.json'
            
            try:
                if s3_service.file_exists(result_key):
                    result_data = s3_service.download_file(result_key)
                    result = json.loads(result_data.decode('utf-8'))
                    result['file_key'] = file_key
                    results.append(result)
                else:
                    results.append({
                        'file_key': file_key,
                        'status': 'processing'
                    })
            except Exception as e:
                logger.warning(f"Error fetching result for {file_key}: {str(e)}")
                results.append({
                    'file_key': file_key,
                    'status': 'error',
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in batch results: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Batch fetch failed',
            'message': str(e)
        }), 500


@results_bp.route('/results/status/<path:file_key>', methods=['GET'])
def check_status(file_key):
    """
    Quick status check without fetching full result
    Useful for polling during processing
    
    Response:
        {
            "success": true,
            "status": "completed|processing|failed",
            "ready": true|false
        }
    """
    try:
        result_key = file_key.replace('uploads/', 'results/').rsplit('.', 1)[0] + '.json'
        
        # Initialize S3 service
        s3_service = S3Service(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION'],
            bucket_name=current_app.config['S3_BUCKET_NAME']
        )
        
        exists = s3_service.file_exists(result_key)
        
        return jsonify({
            'success': True,
            'status': 'completed' if exists else 'processing',
            'ready': exists
        }), 200
        
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

