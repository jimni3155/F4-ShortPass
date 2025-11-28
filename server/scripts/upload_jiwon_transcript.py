"""
김지원 면접 transcript를 S3에 업로드하는 스크립트

Usage:
    cd /home/ec2-user/flex/server
    python scripts/upload_jiwon_transcript.py
"""
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.storage.s3_service import S3Service
from core.config import S3_BUCKET_NAME, AWS_REGION


def upload_transcript_and_resume():
    """김지원 transcript와 resume를 S3에 업로드"""

    data_dir = Path(__file__).resolve().parent.parent / "test_data"

    # 파일 경로
    transcript_path = data_dir / "transcript_jiwon_101.json"
    resume_path = data_dir / "resume_sample_101.json"
    interview_questions_path = data_dir / "interview_questions_101.json"

    print("\n" + "=" * 60)
    print("  김지원 면접 데이터 S3 업로드")
    print("=" * 60)

    print(f"\n  Bucket: {S3_BUCKET_NAME}")
    print(f"  Region: {AWS_REGION}")

    # S3 서비스 초기화
    s3_service = S3Service(bucket_name=S3_BUCKET_NAME, region_name=AWS_REGION)

    interview_id = 101
    applicant_id = 101

    # 1. Transcript 업로드
    if transcript_path.exists():
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript = json.load(f)

        transcript_key = f"interviews/{interview_id}/transcript.json"
        transcript_url = s3_service.upload_json(transcript_key, transcript)
        print(f"\n  [1] Transcript 업로드 완료")
        print(f"      Key: {transcript_key}")
        print(f"      URL: {transcript_url}")
    else:
        print(f"\n  [1] Transcript 파일 없음: {transcript_path}")

    # 2. Resume 업로드
    if resume_path.exists():
        with open(resume_path, "r", encoding="utf-8") as f:
            resume = json.load(f)

        resume_key = f"applicants/{applicant_id}/resume.json"
        resume_url = s3_service.upload_json(resume_key, resume)
        print(f"\n  [2] Resume 업로드 완료")
        print(f"      Key: {resume_key}")
        print(f"      URL: {resume_url}")
    else:
        print(f"\n  [2] Resume 파일 없음: {resume_path}")

    # 3. Interview Questions 업로드
    if interview_questions_path.exists():
        with open(interview_questions_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        questions_key = f"interviews/{interview_id}/questions.json"
        questions_url = s3_service.upload_json(questions_key, questions)
        print(f"\n  [3] Interview Questions 업로드 완료")
        print(f"      Key: {questions_key}")
        print(f"      URL: {questions_url}")
    else:
        print(f"\n  [3] Interview Questions 파일 없음: {interview_questions_path}")

    # 4. 검증 - 다운로드해서 확인
    print("\n" + "-" * 60)
    print("  검증: 업로드된 데이터 확인")
    print("-" * 60)

    downloaded_transcript = s3_service.download_json(f"interviews/{interview_id}/transcript.json")
    if downloaded_transcript:
        segments = downloaded_transcript.get("segments", [])
        print(f"\n  Transcript 검증:")
        print(f"    - Interview ID: {downloaded_transcript.get('interview_id')}")
        print(f"    - Applicant ID: {downloaded_transcript.get('applicant_id')}")
        print(f"    - Segments: {len(segments)}개")
        if segments:
            print(f"    - 첫 번째 질문: {segments[0].get('question_text', '')[:50]}...")

    downloaded_resume = s3_service.download_json(f"applicants/{applicant_id}/resume.json")
    if downloaded_resume:
        print(f"\n  Resume 검증:")
        print(f"    - Applicant Name: {downloaded_resume.get('applicant_name')}")
        print(f"    - Education: {downloaded_resume.get('education', [{}])[0].get('school')}")

    print("\n" + "=" * 60)
    print("  업로드 완료!")
    print("=" * 60)
    print(f"\n  S3 경로:")
    print(f"    - s3://{S3_BUCKET_NAME}/interviews/{interview_id}/transcript.json")
    print(f"    - s3://{S3_BUCKET_NAME}/applicants/{applicant_id}/resume.json")
    print(f"    - s3://{S3_BUCKET_NAME}/interviews/{interview_id}/questions.json")
    print()


if __name__ == "__main__":
    upload_transcript_and_resume()
