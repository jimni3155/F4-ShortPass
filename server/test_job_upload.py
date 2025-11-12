#!/usr/bin/env python3
# server/test_job_upload.py
"""
JD PDF 업로드 플로우 테스트 스크립트
"""
import sys
import os

# Add server directory to path
sys.path.insert(0, '/home/ec2-user/flex/server')

from db.database import SessionLocal
from services.job_service import JobService
import asyncio


async def test_pdf_upload():
    """
    샘플 PDF로 전체 플로우 테스트

    전체 플로우:
    1. PDF 생성 (간단한 텍스트 PDF)
    2. S3 업로드
    3. PDF 파싱
    4. 청크 분할
    5. 임베딩 생성
    6. DB 저장
    """
    print("\n" + "="*60)
    print("JD PDF Upload Flow Test")
    print("="*60 + "\n")

    # 테스트용 간단한 PDF 생성 (reportlab 사용)
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import io

        print("[1/6] Creating test PDF...")

        # PDF 버퍼 생성
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        # 텍스트 작성
        c.drawString(100, 750, "Job Description - Backend Developer")
        c.drawString(100, 730, "-" * 50)

        y_position = 700
        jd_text = [
            "",
            "Position: Senior Backend Developer",
            "",
            "Requirements:",
            "- 5+ years of experience in Python development",
            "- Strong knowledge of FastAPI, Django, or Flask",
            "- Experience with PostgreSQL and Redis",
            "- Understanding of microservices architecture",
            "- Experience with AWS services (EC2, S3, RDS)",
            "",
            "Responsibilities:",
            "- Design and implement RESTful APIs",
            "- Optimize database queries and improve performance",
            "- Collaborate with frontend developers",
            "- Write unit tests and maintain code quality",
            "",
            "Preferred Qualifications:",
            "- Experience with Docker and Kubernetes",
            "- Knowledge of CI/CD pipelines",
            "- Experience with message queues (RabbitMQ, Kafka)",
            "",
            "Benefits:",
            "- Competitive salary",
            "- Flexible working hours",
            "- Health insurance",
            "- Learning and development budget",
        ]

        for line in jd_text:
            c.drawString(100, y_position, line)
            y_position -= 20
            if y_position < 100:
                c.showPage()
                y_position = 750

        c.save()

        pdf_content = buffer.getvalue()
        buffer.close()

        print(f"✓ Test PDF created: {len(pdf_content)} bytes")

    except ImportError:
        print("⚠ reportlab not installed, using dummy PDF")
        # 간단한 더미 PDF (실제로는 작동하지 않을 수 있음)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        print("⚠ Using minimal dummy PDF for testing structure only")

    # DB 세션 생성
    print("\n[2/6] Creating database session...")
    db = SessionLocal()

    try:
        # JobService 인스턴스 생성
        print("\n[3/6] Initializing JobService...")
        job_service = JobService()

        # PDF 처리
        print("\n[4/6] Processing JD PDF...")
        job = await job_service.process_jd_pdf(
            db=db,
            pdf_content=pdf_content,
            file_name="test_backend_developer.pdf",
            company_id=1,
            title="Senior Backend Developer"
        )

        print(f"\n[5/6] Job created successfully!")
        print(f"  - Job ID: {job.id}")
        print(f"  - Title: {job.title}")
        print(f"  - Company ID: {job.company_id}")

        # Job 조회
        print(f"\n[6/6] Retrieving job with chunks...")
        job_data = job_service.get_job_with_chunks(db, job.id)

        if job_data:
            print(f"\n✓ Job retrieved successfully:")
            print(f"  - Job ID: {job_data['job_id']}")
            print(f"  - Title: {job_data['title']}")
            print(f"  - Total chunks: {job_data['total_chunks']}")
            print(f"  - Description length: {len(job_data['description'])} chars")

            # 첫 번째 청크 출력
            if job_data['chunks']:
                first_chunk = job_data['chunks'][0]
                print(f"\n  First chunk preview:")
                print(f"    - Chunk ID: {first_chunk['chunk_id']}")
                print(f"    - Has embedding: {first_chunk['has_embedding']}")
                print(f"    - Text preview: {first_chunk['chunk_text'][:100]}...")

        print(f"\n{'='*60}")
        print("✓ Test completed successfully!")
        print(f"{'='*60}\n")

        return job.id

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        db.close()


async def test_vector_search(job_id: int):
    """
    벡터 검색 테스트
    """
    print(f"\n{'='*60}")
    print("Vector Search Test")
    print(f"{'='*60}\n")

    db = SessionLocal()

    try:
        job_service = JobService()

        # 검색 쿼리
        queries = [
            "Python FastAPI experience",
            "AWS cloud services",
            "Docker Kubernetes"
        ]

        for query in queries:
            print(f"\nSearching for: '{query}'")
            results = job_service.search_similar_chunks(
                db=db,
                query_text=query,
                top_k=3,
                job_id=job_id
            )

            if results:
                print(f"Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. Similarity: {result['similarity']:.4f}")
                    print(f"     Text: {result['chunk_text'][:80]}...")
            else:
                print("  No results found")

        print(f"\n{'='*60}")
        print("✓ Vector search test completed!")
        print(f"{'='*60}\n")

    except Exception as e:
        print(f"\n✗ Search test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()


async def main():
    """메인 테스트 함수"""
    # PDF 업로드 테스트
    job_id = await test_pdf_upload()

    if job_id:
        # 벡터 검색 테스트
        await test_vector_search(job_id)
    else:
        print("Skipping vector search test due to upload failure")


if __name__ == "__main__":
    asyncio.run(main())
