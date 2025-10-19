import json
import os
import boto3
import tempfile
from typing import Dict, Any
import google.generativeai as genai

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        record = event['Records'][0]
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        
        print(f"Processing audio file: {object_key} from bucket: {bucket_name}")
        
        audio_data = download_audio_from_s3(bucket_name, object_key)
        transcript = transcribe_audio(audio_data)
        latex_output = convert_to_latex(transcript)
        
        result = {
            'transcript': transcript,
            'latex': latex_output,
            'audio_key': object_key,
            'status': 'success'
        }
        
        result_key = object_key.replace('uploads/', 'results/').replace('.webm', '.json')
        store_result_to_s3(bucket_name, result_key, result)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        print(f"Error processing audio: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'status': 'failed'
            })
        }


def download_audio_from_s3(bucket: str, key: str) -> bytes:
    response = s3_client.get_object(Bucket=bucket, Key=key)
    return response['Body'].read()


def transcribe_audio(audio_data: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as temp_audio:
        temp_audio.write(audio_data)
        temp_audio_path = temp_audio.name
    
    try:
        audio_file = genai.upload_file(path=temp_audio_path)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = "Transcribe this audio accurately. Focus on mathematical expressions and technical terms."
        response = model.generate_content([prompt, audio_file])
        return response.text.strip()
    finally:
        os.unlink(temp_audio_path)


def convert_to_latex(transcript: str) -> str:
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""Convert the following mathematical expression to LaTeX code. 
Return ONLY the LaTeX code without explanation or markdown formatting: {transcript}"""
    
    response = model.generate_content(prompt)
    latex_code = response.text.strip()
    latex_code = latex_code.replace('```latex', '').replace('```', '').strip()
    return latex_code


def store_result_to_s3(bucket: str, key: str, result: Dict[str, Any]) -> None:
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(result),
        ContentType='application/json'
    )
    print(f"Result stored to s3://{bucket}/{key}")

