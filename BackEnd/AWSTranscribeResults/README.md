# AWS Transcribe Results

This directory contains transcription results from AWS Transcribe.

## File Format

Each transcription creates a JSON file: `{timestamp}_transcript.json`

Example: `20241019_143022_transcript.json`

## JSON Structure

```json
{
  "timestamp": "20241019_143022",
  "job_name": "speaktex_20241019_143022",
  "transcript_text": "x squared plus two x plus one",
  "full_result": {
    // Complete AWS Transcribe response
  }
}
```

## Key Fields

- **`transcript_text`**: The transcribed speech as plain text (use this for LaTeX conversion)
- **`timestamp`**: When the transcription was created
- **`job_name`**: AWS Transcribe job identifier
- **`full_result`**: Complete AWS response with timing, confidence scores, etc.

## Usage

After recording:
1. Audio uploads to S3
2. Transcription job runs (30-60 seconds)
3. Result saved here automatically
4. Frontend receives the transcript text

## Viewing Results

```powershell
# View latest transcript
cd BackEnd/AWSTranscribeResults
Get-ChildItem | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | Get-Content | ConvertFrom-Json
```

## Note

These files are auto-generated. Don't edit manually.

