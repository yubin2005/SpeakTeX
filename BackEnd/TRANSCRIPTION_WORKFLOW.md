# AWS Transcribe Integration - Complete Workflow

## Overview

**Complete automated flow:**
1. Frontend records audio using MediaRecorder
2. Frontend gets presigned S3 upload URL from Lambda
3. Frontend uploads webm directly to S3
4. Frontend triggers AWS Transcribe job
5. Transcription completes (30-60 seconds)
6. Transcript saved to `BackEnd/AWSTranscribeResults/`

**No manual steps required.** Everything happens automatically after clicking record/stop.

## Architecture

```
Frontend (MediaRecorder)
    ↓
Lambda: get_upload_url → Presigned URL
    ↓
Frontend uploads to S3
    ↓
Lambda: transcribe_audio → Start AWS Transcribe job
    ↓
Poll until complete (30-60s)
    ↓
Download transcript from S3
    ↓
Save to BackEnd/AWSTranscribeResults/{timestamp}_transcript.json
    ↓
Return transcript text to frontend
```

## Setup

### 1. Install Dependencies

```powershell
cd BackEnd
pip install -r requirements.txt
```

Ensure you have:
- `boto3` - AWS SDK
- `requests` - HTTP requests for downloading transcripts
- `python-dotenv` - Environment variables

### 2. Configure AWS

Create `BackEnd/.env`:

```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-2
S3_BUCKET_NAME=your-bucket-name
```

### 3. Verify AWS Permissions

Your AWS IAM user needs:
- **S3**: `PutObject`, `GetObject`, `ListBucket`
- **Transcribe**: `StartTranscriptionJob`, `GetTranscriptionJob`

## Usage

### Start Services

**Terminal 1 - Lambda Server:**
```powershell
cd BackEnd/lambda
python local_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd FrontEnd
npm run dev
```

### Record Audio

1. Open `http://localhost:5173`
2. Click microphone button
3. Speak your math expression
4. Click stop

**Console output:**
```
Step 1: Getting presigned upload URL from Lambda...
Step 2: Uploading audio directly to S3...
✓ Audio uploaded successfully to S3!
✓ File key: audio/recordings/20241019_123456.webm
Step 3: Starting AWS Transcribe job...
  Status: IN_PROGRESS (5s elapsed)
  Status: IN_PROGRESS (10s elapsed)
  ...
  Status: COMPLETED (45s elapsed)
✓ Transcription completed!
✓ Transcript: "x squared plus two x plus one"
✓ Saved to: BackEnd/AWSTranscribeResults/20241019_123456_transcript.json
```

### View Results

Check the transcript file:
```powershell
cd BackEnd/AWSTranscribeResults
cat 20241019_123456_transcript.json
```

**JSON structure:**
```json
{
  "timestamp": "20241019_123456",
  "job_name": "speaktex_20241019_123456",
  "transcript_text": "x squared plus two x plus one",
  "full_result": {
    "jobName": "...",
    "results": {
      "transcripts": [
        {
          "transcript": "x squared plus two x plus one"
        }
      ],
      "items": [...]
    }
  }
}
```

## Testing

### Test Transcription Only

If you already have a file in S3:

```powershell
cd BackEnd/lambda
python transcribe_audio.py audio/recordings/20241019_123456.webm
```

Or let it find the most recent:
```powershell
python transcribe_audio.py
```

### Test Complete Flow

```powershell
cd BackEnd
python test_recording_flow.py
```

This tests:
1. Generate presigned upload URL
2. Upload test file to S3
3. Download from S3
4. Verify file saved

## Files

### Lambda Functions
- **`lambda/get_upload_url.py`** - Generates S3 presigned upload URLs
- **`lambda/transcribe_audio.py`** - Starts and monitors AWS Transcribe jobs
- **`lambda/local_server.py`** - Local HTTP server for testing

### Frontend
- **`FrontEnd/src/components/AudioRecorder/index.jsx`** - Handles recording + upload + transcription

### Output
- **`BackEnd/AWSTranscribeResults/*.json`** - Transcription results

## Timing

- **Upload to S3**: 1-2 seconds
- **Transcribe job**: 30-60 seconds (depends on audio length)
- **Total time**: ~35-65 seconds from click stop to transcript

## Troubleshooting

### "Missing AWS credentials"
Check `BackEnd/.env` has valid credentials.

### "Access Denied" from S3
Verify IAM permissions for S3 bucket access.

### "Access Denied" from Transcribe
Verify IAM permissions for AWS Transcribe service.

### Transcription times out
Increase timeout in `transcribe_audio.py`:
```python
poll_result = poll_transcription_job(job_name, max_wait_seconds=600)  # 10 minutes
```

### "Media format not supported"
AWS Transcribe supports: webm, mp3, mp4, wav, flac, ogg, amr, webm
Frontend uses webm by default (should work).

### Transcription is empty
- Check audio actually recorded (file size > 0)
- Verify audio contains speech (not silent)
- Try speaking more clearly

## Next Steps

After transcription works, the next phase is:
1. Take the transcript text
2. Send to Gemini API to convert to LaTeX
3. Display the LaTeX in the frontend

Transcription gives you: `"x squared plus two x plus one"`
Gemini will convert to: `$x^2 + 2x + 1$`

