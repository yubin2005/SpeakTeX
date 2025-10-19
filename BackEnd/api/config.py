"""
Configuration Management
Purpose: Centralized configuration for the SpeakTeX API
Loads environment variables and provides configuration classes
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Base configuration class with common settings"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # CORS Configuration
    CORS_ORIGIN = os.environ.get('CORS_ORIGIN', 'http://localhost:5173')
    
    # File Upload Configuration
    MAX_AUDIO_SIZE_MB = int(os.environ.get('MAX_AUDIO_SIZE_MB', 10))
    MAX_CONTENT_LENGTH = MAX_AUDIO_SIZE_MB * 1024 * 1024  # Convert to bytes
    ALLOWED_AUDIO_EXTENSIONS = {'webm', 'wav', 'mp3', 'ogg'}
    
    # AWS Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-2')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
    DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME', 'speaktex-history')
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'
    
    # Request Configuration
    REQUEST_TIMEOUT = 30  # seconds
    
    # Retry Configuration (exponential backoff)
    MAX_RETRIES = 3
    RETRY_DELAYS = [1, 2, 4]  # seconds
    
    # Cache Configuration (in-memory LRU cache)
    CACHE_MAX_SIZE = 100
    CACHE_TTL = 3600  # seconds (1 hour)
    
    @staticmethod
    def validate_config():
        """
        Validate that all required configuration variables are set
        Raises ValueError if critical configuration is missing
        """
        required_vars = {
            'AWS_ACCESS_KEY_ID': Config.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': Config.AWS_SECRET_ACCESS_KEY,
            'S3_BUCKET_NAME': Config.S3_BUCKET_NAME,
            'DYNAMODB_TABLE_NAME': Config.DYNAMODB_TABLE_NAME,
            'GEMINI_API_KEY': Config.GEMINI_API_KEY,
        }
        
        missing_vars = [key for key, value in required_vars.items() if not value]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please check your .env file or environment configuration."
            )


class DevelopmentConfig(Config):
    """Development environment specific configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production environment specific configuration"""
    DEBUG = False
    TESTING = False
    
    # Override with stricter production settings
    MAX_AUDIO_SIZE_MB = 5
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


class TestingConfig(Config):
    """Testing environment specific configuration"""
    DEBUG = True
    TESTING = True
    
    # Use mock values for testing
    S3_BUCKET_NAME = 'test-bucket'


# Configuration dictionary for easy access
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Get configuration object based on FLASK_ENV environment variable
    
    Returns:
        Config class instance
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)

