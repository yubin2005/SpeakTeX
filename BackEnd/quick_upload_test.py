"""
Quick Upload Test
Run this after setting up your .env file to quickly test S3 upload
Usage: python quick_upload_test.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_file = Path(__file__).parent / '.env'
if not env_file.exists():
    print("ERROR: .env file not found!")
    print(f"Expected location: {env_file}")
    print("Copy .env.example to .env and add your AWS credentials")
    exit(1)

load_dotenv(env_file)

# Import after loading .env
import sys
sys.path.insert(0, str(Path(__file__).parent / 'lambda'))
from upload_audio import lambda_handler

# Test the upload
print("Testing S3 upload...")
print(f"Bucket: {os.getenv('S3_BUCKET_NAME')}")
print(f"Region: {os.getenv('AWS_REGION')}")
print()

event = {'file_path': 'temp_audio.webm'}
response = lambda_handler(event)

print(f"Status: {response['statusCode']}")
print(f"Response: {response['body']}")


