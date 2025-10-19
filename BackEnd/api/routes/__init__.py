"""
Routes Package
Contains all API route blueprints for the SpeakTeX application
"""

from .upload import upload_bp
from .results import results_bp

__all__ = ['upload_bp', 'results_bp']

