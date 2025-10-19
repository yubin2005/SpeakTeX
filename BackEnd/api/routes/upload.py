"""
Upload Routes
Purpose: Generate presigned S3 URLs for direct audio file uploads from frontend
Benefits: Reduces API server load, enables faster uploads, improves scalability
"""

from flask import Blueprint, request, jsonify, current_app
from services.s3_service import S3Service
import logging
import uuid
from datetime import datetime

upload_bp = Blueprint('upload', __name__)
logger = logging.getLogger(__name__)


@upload_bp.route('/upload/presigned-url', methods=['POST'])
def generate_presigned_url():
    """
    Generate presigned S3 URL for direct audio upload
    
    Request body:
        {
            "filename": "audio.webm",
            "content_type": "audio/webm"
        }
    
    Response:
        {
            "success": true,
            "upload_url": "https://s3.amazonaws.com/...",
            "file_key": "uploads/uuid/audio.webm",
            "expires_in": 300
        }
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Missing request body'
            }), 400
        
        filename = data.get('filename', 'audio.webm')
        content_type = data.get('content_type', 'audio/webm')
        
        # Validate content type
        allowed_types = ['audio/webm', 'audio/wav', 'audio/mp3', 'audio/ogg']
        if content_type not in allowed_types:
            return jsonify({
                'success': False,
                'error': f'Invalid content type. Allowed: {", ".join(allowed_types)}'
            }), 400
        
        # Generate unique file key
        file_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_key = f"uploads/{timestamp}_{file_id}/{filename}"
        
        # Initialize S3 service
        s3_service = S3Service(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION'],
            bucket_name=current_app.config['S3_BUCKET_NAME']
        )
        
        # Generate presigned URL (valid for 5 minutes)
        presigned_data = s3_service.generate_presigned_upload_url(
            file_key=file_key,
            content_type=content_type,
            expires_in=300
        )
        
        logger.info(f"Generated presigned URL for file: {file_key}")
        
        return jsonify({
            'success': True,
            'upload_url': presigned_data['url'],
            'file_key': file_key,
            'expires_in': 300,
            'method': 'PUT'
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate upload URL',
            'message': str(e)
        }), 500


@upload_bp.route('/upload/direct', methods=['POST'])
def direct_upload():
    """
    Direct upload endpoint (alternative to presigned URL)
    Accepts audio file and uploads to S3 through API server
    
    Note: Presigned URL method is preferred for better performance
    """
    try:
        # Check if file is in request
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No audio file provided'
            }), 400
        
        audio_file = request.files['audio']
        
        # Validate file
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
        
        # Validate file size
        audio_file.seek(0, 2)  # Seek to end
        file_size = audio_file.tell()
        audio_file.seek(0)  # Reset to beginning
        
        max_size = current_app.config['MAX_CONTENT_LENGTH']
        if file_size > max_size:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size: {max_size / (1024*1024)}MB'
            }), 400
        
        # Generate unique file key
        file_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        file_key = f"uploads/{timestamp}_{file_id}/{audio_file.filename}"
        
        # Initialize S3 service
        s3_service = S3Service(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=current_app.config['AWS_REGION'],
            bucket_name=current_app.config['S3_BUCKET_NAME']
        )
        
        # Upload to S3
        s3_service.upload_file(
            file_data=audio_file.read(),
            file_key=file_key,
            content_type=audio_file.content_type or 'audio/webm'
        )
        
        logger.info(f"Successfully uploaded file: {file_key}")
        
        return jsonify({
            'success': True,
            'file_key': file_key,
            'message': 'File uploaded successfully. Processing will begin shortly.'
        }), 200
        
    except Exception as e:
        logger.error(f"Error in direct upload: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Upload failed',
            'message': str(e)
        }), 500

