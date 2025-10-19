# SpeakTeX Backend

## Overview
SpeakTeX backend consists of two main components:
1. **Lambda Function**: Serverless audio processing with Gemini API
2. **Flask API**: Upload management and result retrieval

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│  Flask API   │────▶│     S3      │
│   (React)   │     │  (presigned) │     │   Bucket    │
└─────────────┘     └──────────────┘     └─────────────┘
                                                 │
                                                 │ triggers
                                                 ▼
                                          ┌─────────────┐
                                          │   Lambda    │
                                          │  Function   │
                                          └─────────────┘
                                                 │
                                                 │ calls
                                                 ▼
                                          ┌─────────────┐
                                          │  Gemini API │
                                          │ (Transcribe │
                                          │  + LaTeX)   │
                                          └─────────────┘
                                                 │
                                                 │ stores
                                                 ▼
                                          ┌─────────────┐
                                          │     S3      │
                                          │  (results)  │
                                          └─────────────┘
```

## Directory Structure

```
backend/
├── lambda/                    # AWS Lambda function
│   ├── audio_processor.py     # Main Lambda handler
│   ├── requirements.txt       # Lambda dependencies
│   └── README.md              # Deployment guide
├── api/                       # Flask REST API
│   ├── app.py                 # Main Flask application
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # API dependencies
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── upload.py          # Presigned URL generation
│   │   └── results.py         # Result fetching
│   └── services/
│       ├── __init__.py
│       ├── s3_service.py      # S3 operations
│       └── aws_config.py      # AWS SDK configuration
├── app/                       # Legacy Flask structure (can be deprecated)
├── .env                       # Environment variables (create from .env.example)
├── .env.example               # Environment template
├── .gitignore                 # Git ignore patterns
└── README.md                  # This file
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- AWS Account with S3 and Lambda access
- Google Gemini API key

### 1. Environment Configuration

Create `.env` file in the backend root:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_REGION=us-east-2
S3_BUCKET_NAME=speaktex-audio-storage

# Gemini API
GEMINI_API_KEY=your_gemini_key_here

# Optional
FLASK_ENV=development
CORS_ORIGIN=http://localhost:5173
MAX_AUDIO_SIZE_MB=10
```

### 2. Install API Dependencies

```powershell
cd backend/api
pip install -r requirements.txt
```

### 3. Run Flask API (Development)

```powershell
cd backend/api
python app.py
```

API will be available at `http://localhost:5000`

### 4. Deploy Lambda Function

See `lambda/README.md` for detailed Lambda deployment instructions.

## API Endpoints

### Health Check
```
GET /api/health
Response: { "status": "healthy", "service": "speaktex-api", ... }
```

### Generate Presigned Upload URL
```
POST /api/upload/presigned-url
Body: { "filename": "audio.webm", "content_type": "audio/webm" }
Response: { "success": true, "upload_url": "https://...", "file_key": "uploads/..." }
```

### Direct Upload (Alternative)
```
POST /api/upload/direct
Body: FormData with 'audio' file
Response: { "success": true, "file_key": "uploads/..." }
```

### Get Processing Result
```
GET /api/results/<file_key>
Response: { "success": true, "status": "completed", "transcript": "...", "latex": "..." }
```

### Check Processing Status
```
GET /api/results/status/<file_key>
Response: { "success": true, "status": "completed|processing", "ready": true|false }
```

### Batch Results
```
POST /api/results/batch
Body: { "file_keys": ["uploads/...", ...] }
Response: { "success": true, "results": [...] }
```

## Workflow

### Upload Flow (Presigned URL)
1. Frontend requests presigned URL from `/api/upload/presigned-url`
2. API generates S3 presigned URL (valid for 5 minutes)
3. Frontend uploads audio directly to S3 using presigned URL
4. S3 triggers Lambda function automatically
5. Lambda processes audio and stores results
6. Frontend polls `/api/results/status/<file_key>` until complete
7. Frontend fetches result from `/api/results/<file_key>`

### Processing Flow (Lambda)
1. S3 upload triggers Lambda function
2. Lambda downloads audio from S3
3. Audio transcribed using Gemini API
4. Transcript converted to LaTeX using Gemini API
5. Result stored to S3 as JSON (`results/` prefix)

## Configuration

### Flask Configuration (`config.py`)
- `DevelopmentConfig`: Debug enabled, verbose logging
- `ProductionConfig`: Stricter limits, production optimizations
- `TestingConfig`: Mock values for testing

### AWS S3 Structure
```
s3://speaktex-audio-storage/
  uploads/              # Raw audio files (triggers Lambda)
    20241018_120000_uuid/
      audio.webm
  results/              # Processing results (JSON)
    20241018_120000_uuid/
      audio.json
```

## Error Handling

### API Error Responses
- `400`: Bad request (invalid input)
- `404`: Resource not found
- `500`: Internal server error
- `503`: Service unavailable (rate limits)

### Lambda Error Handling
- Retries: Automatic with exponential backoff
- Dead Letter Queue: Failed events stored for analysis
- CloudWatch Logs: All processing logged

## Security

### Environment Variables
- **Never commit `.env` file**
- Use AWS Secrets Manager for production
- Rotate API keys regularly

### CORS Configuration
- Development: `http://localhost:5173`
- Production: Whitelist only your frontend domain

### S3 Security
- Bucket is private (no public access)
- Presigned URLs for temporary access
- IAM roles with least privilege

## Monitoring

### CloudWatch Metrics
- Lambda invocations and duration
- API request counts and latencies
- Error rates and types

### Logging
- Lambda: CloudWatch Logs at `/aws/lambda/speaktex-audio-processor`
- API: Console output (development) or log files (production)

## Production Deployment

### Flask API (Using Gunicorn)
```powershell
cd backend/api
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Environment Variables
Set in production environment:
- `FLASK_ENV=production`
- `CORS_ORIGIN=https://yourdomain.com`

### Recommended Infrastructure
- AWS EC2 or Elastic Beanstalk for Flask API
- AWS Lambda for audio processing
- AWS S3 for storage
- CloudFront for CDN (optional)

## Development Tips

### Local Testing
```powershell
# Test health endpoint
curl http://localhost:5000/api/health

# Test presigned URL generation
curl -X POST http://localhost:5000/api/upload/presigned-url \
  -H "Content-Type: application/json" \
  -d '{"filename": "test.webm", "content_type": "audio/webm"}'
```

### Debug Mode
Set `FLASK_ENV=development` for:
- Auto-reload on code changes
- Detailed error messages
- Debug toolbar

## Troubleshooting

### Common Issues

**Issue**: "Missing required environment variables"
- **Solution**: Create `.env` file with all required variables

**Issue**: "S3 access denied"
- **Solution**: Verify AWS credentials and IAM permissions

**Issue**: "Lambda timeout"
- **Solution**: Increase Lambda timeout (max 15 minutes)

**Issue**: "Gemini API rate limit"
- **Solution**: Implement exponential backoff, check API quotas

## Testing

### Unit Tests
```powershell
pytest tests/
```

### Integration Tests
```powershell
pytest tests/integration/
```

### Manual API Testing
Use Postman collection in `/docs/postman_collection.json`

## License
MIT License - See LICENSE file for details

## Support
For issues and questions, please open a GitHub issue or contact the development team.

