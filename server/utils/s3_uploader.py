# utils/s3_uploader.py
import boto3
from botocore.exceptions import NoCredentialsError
import os
import uuid
from dotenv import load_dotenv

# 1. 현재 서버를 실행한 위치(Current Working Directory) 확인
current_work_dir = os.getcwd()
env_path = os.path.join(current_work_dir, ".env")

# 2. .env 로드 (override=True로 기존 환경변수 무시하고 덮어쓰기)
is_loaded = load_dotenv(dotenv_path=env_path, override=True)
print(f" [DEBUG] 로드 성공 여부: {is_loaded}")

# 3. 값 확인
AWS_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # 기본값 설정

# 값이 비어있으면 터미널에 경고를 띄움
if not AWS_BUCKET_NAME:
    print("❌ [경고] AWS_BUCKET_NAME이 없습니다! .env 내용을 확인하세요.")
else:
    print(f"✅ [성공] 버킷 이름 로드됨: {AWS_BUCKET_NAME}")


def upload_file_and_get_url(file_path: str, folder="interviews") -> str:
    # (기존 코드와 동일)
    if not AWS_BUCKET_NAME:
        print("❌ [FATAL] AWS 환경변수가 로드되지 않아 업로드를 중단합니다.")
        return None

    s3 = boto3.client(
        's3',
        region_name=AWS_REGION
    )

    file_name = os.path.basename(file_path)
    unique_key = f"{folder}/{uuid.uuid4()}_{file_name}"

    try:
        s3.upload_file(file_path, AWS_BUCKET_NAME, unique_key)
        
        url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_BUCKET_NAME, 'Key': unique_key},
            ExpiresIn=3600
        )
        return url

    except Exception as e:
        print(f"S3 업로드 오류: {e}")
        return None