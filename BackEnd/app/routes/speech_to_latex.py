from flask import request, jsonify
from app.routes import api_bp
from app.services import gemini_service

@api_bp.route('/speech-to-latex', methods=['POST'])
def speech_to_latex():
    # Endpoint implementation will go here
    pass
