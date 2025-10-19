# Lambda Function: Audio Processor

## Overview
This Lambda function processes audio files uploaded to S3, transcribes them using Google's Gemini API, converts the transcript to LaTeX format, and stores the results back to S3.

## Architecture Flow
1. Audio file uploaded to S3 (triggers Lambda)
2. Lambda downloads audio from S3
3. Audio transcribed using Gemini API
4. Transcript converted to LaTeX using Gemini API
5. Results stored back to S3 as JSON

## Prerequisites
- AWS Account with Lambda and S3 access
- Google Gemini API key
- Python 3.11 or later

## Environment Variables
Configure these in Lambda function settings:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `AWS_REGION`: AWS region (automatically set by Lambda)

## Deployment Instructions

### Step 1: Prepare Deployment Package
```bash
# Navigate to lambda directory
cd backend/lambda

# Create package directory
mkdir -p package

# Install dependencies
pip install -r requirements.txt -t package/

# Copy function code
cp audio_processor.py package/

# Create deployment package
cd package
zip -r ../audio_processor.zip .
cd ..
```

### Step 2: Create Lambda Function
```bash
# Create Lambda function using AWS CLI
aws lambda create-function \
  --function-name speaktex-audio-processor \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-s3-role \
  --handler audio_processor.lambda_handler \
  --zip-file fileb://audio_processor.zip \
  --timeout 60 \
  --memory-size 512 \
  --environment Variables="{GEMINI_API_KEY=your_api_key_here}"
```

### Step 3: Configure S3 Trigger
```bash
# Add S3 trigger permission to Lambda
aws lambda add-permission \
  --function-name speaktex-audio-processor \
  --statement-id s3-trigger \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::speaktex-audio-storage
```

### Step 4: Configure S3 Event Notification
Add this configuration to your S3 bucket:
```json
{
  "LambdaFunctionConfigurations": [
    {
      "LambdaFunctionArn": "arn:aws:lambda:REGION:ACCOUNT_ID:function:speaktex-audio-processor",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "uploads/"
            }
          ]
        }
      }
    }
  ]
}
```

## IAM Role Requirements
Lambda execution role needs these permissions:
- `s3:GetObject` - Download audio files
- `s3:PutObject` - Store results
- `logs:CreateLogGroup` - CloudWatch logging
- `logs:CreateLogStream` - CloudWatch logging
- `logs:PutLogEvents` - CloudWatch logging

## Testing
Test the function with this sample S3 event:
```json
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "speaktex-audio-storage"
        },
        "object": {
          "key": "uploads/test-audio.webm"
        }
      }
    }
  ]
}
```

## Monitoring
- View logs in CloudWatch: `/aws/lambda/speaktex-audio-processor`
- Monitor invocation metrics in Lambda console
- Check S3 bucket for result files in `results/` prefix

## Troubleshooting
- **Timeout errors**: Increase Lambda timeout (max 15 minutes)
- **Memory errors**: Increase Lambda memory allocation
- **API errors**: Check Gemini API key and rate limits
- **S3 errors**: Verify IAM permissions and bucket names

## Cost Optimization
- Use S3 Intelligent-Tiering for audio storage
- Set lifecycle policy to delete old uploads
- Monitor Lambda duration and optimize cold starts
- Consider provisioned concurrency for consistent latency

