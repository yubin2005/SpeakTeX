# SpeakTeX Backend Tests

Test suite for verifying AWS services and API connectivity.

## Test Files

### 1. `test_aws_credentials.py`
Tests basic AWS credential validity and service access.

**What it tests:**
- S3 service connectivity
- AWS Transcribe service connectivity
- Lists available buckets and transcription jobs

**Run:**
```bash
python tests/test_aws_credentials.py
```

**Expected output:**
```
✅ S3 Connection: SUCCESS
   Found bucket: speaktex-audio-storage
✅ Transcribe Connection: SUCCESS
```

---

### 2. `test_s3_operations.py`
Tests complete S3 upload/download workflow.

**What it tests:**
- Create local test file
- Upload to S3
- Download from S3
- Verify content integrity
- Cleanup (delete test file)

**Run:**
```bash
python tests/test_s3_operations.py
```

**Expected output:**
```
Step 1: Creating test file... ✅
Step 2: Uploading to S3... ✅
Step 3: Downloading from S3... ✅
Step 4: Verifying content... ✅
Step 5: Cleaning up... ✅
All S3 operations working!
```

---

### 3. `test_gemini_api.py`
Tests Gemini API connectivity and LaTeX conversion.

**What it tests:**
- HTTP connection to Gemini API
- Text generation capability
- LaTeX conversion accuracy

**Run:**
```bash
python tests/test_gemini_api.py
```

**Expected output:**
```
Sending request: "Convert this to LaTeX: x squared"
Response received ✅
Generated text: x^2
✅ Gemini API working!
```

---

### 4. `test_transcribe_job.py`
Tests AWS Transcribe job creation.

**What it tests:**
- Upload test audio to S3
- Start transcription job
- Verify job appears in job list
- Cleanup test files

**Note:** Uses a dummy audio file, so jobs may fail quickly. This test only verifies we can START jobs, not complete them.

**Run:**
```bash
python tests/test_transcribe_job.py
```

**Expected output:**
```
Step 1: Uploading test audio... ✅
Step 2: Starting transcribe job... ✅
Job Name: test-job-1234567890
Initial Status: IN_PROGRESS (or QUEUED)
✅ Transcribe API working!
```

---

### 5. `test_lambda_trigger.py`
Tests Lambda function invocation permissions.

**What it tests:**
- Lambda invocation permissions
- Mock S3 event handling
- Lambda function existence

**Note:** Lambda function may not exist yet. Test will pass if we have invocation permissions.

**Run:**
```bash
python tests/test_lambda_trigger.py
```

**Expected output (if Lambda exists):**
```
Response Status: 200
✅ Lambda invoked successfully!
```

**Or (if Lambda doesn't exist yet):**
```
❌ Lambda function not found (this is OK, we'll create it later)
   But we have permission to invoke Lambda functions ✅
✅ Lambda invocation permission confirmed
```

---

## Running All Tests

To run all tests sequentially:

```bash
cd backend
python tests/test_aws_credentials.py
python tests/test_s3_operations.py
python tests/test_gemini_api.py
python tests/test_transcribe_job.py
python tests/test_lambda_trigger.py
```

Or create a test runner script to run them all at once.

---

## Requirements

Install required packages:

```bash
pip install boto3 requests
```

---

## Credentials

All tests load credentials from environment variables via the `.env` file in the `backend/` directory.

Required environment variables:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key
- `AWS_REGION`: AWS region (default: `us-east-2`)
- `S3_BUCKET_NAME`: Your S3 bucket name (default: `speaktex-audio-storage`)
- `GEMINI_API_KEY`: Your Google Gemini API key

**Setup:**

1. Create `backend/.env` file with your actual credentials:
```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-2
S3_BUCKET_NAME=speaktex-audio-storage
GEMINI_API_KEY=your_gemini_api_key_here
```

2. Ensure `.env` is in `.gitignore` (it should be by default)

**⚠️ Security Note:** Never commit the `.env` file with real credentials. Use `.env.example` as a template.

---

## Troubleshooting

### Test 1 fails (AWS Credentials)
- Verify credentials are correct
- Check internet connectivity
- Verify IAM permissions

### Test 2 fails (S3 Operations)
- Ensure bucket `speaktex-audio-storage` exists
- Check S3 permissions (PutObject, GetObject, DeleteObject)
- Verify bucket is in `us-east-2` region

### Test 3 fails (Gemini API)
- Check API key is valid
- Verify internet connectivity
- Check Gemini API quotas/rate limits

### Test 4 fails (Transcribe)
- Verify Transcribe service is enabled in AWS account
- Check IAM permissions for Transcribe
- Note: Jobs may fail due to dummy audio (this is expected)

### Test 5 fails (Lambda)
- If function not found: This is OK before deployment
- If access denied: Check IAM permissions for Lambda invocation
- If function error: Check Lambda logs in CloudWatch

---

## Next Steps

After all tests pass:
1. Deploy Lambda function (see `backend/lambda/README.md`)
2. Configure S3 event trigger for Lambda
3. Deploy Flask API (see `backend/api/README.md`)
4. Integrate frontend with API
5. Test end-to-end workflow

