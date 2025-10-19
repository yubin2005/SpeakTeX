import boto3
from dotenv import load_dotenv
import os

load_dotenv()

try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
    
    print(f"✅ AWS S3 连接成功!")
    print(f"📦 Bucket: {bucket_name}")
    print(f"🌍 Region: {os.getenv('AWS_REGION')}")
    
    if 'Contents' in response:
        print(f"\n📁 最近上传的文件:")
        for obj in response['Contents'][:5]:
            print(f"  - {obj['Key']} ({obj['Size']} bytes)")
    else:
        print("\n📁 Bucket 目前是空的")
        
except Exception as e:
    print(f"❌ 连接失败: {e}")