from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api')

from app.routes import speech_to_latex, health
