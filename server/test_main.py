# server/test_main.py
"""
JD Persona 기능 테스트용 간단한 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="JD-Persona Test Server",
    description="JD 기반 페르소나 생성 API 테스트 서버",
    version="1.0.0",
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 개발 서버
        "http://localhost:3000",  # React 개발 서버
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JD Persona API 포함
try:
    from api import jd_persona
    app.include_router(jd_persona.router, prefix="/api/v1", tags=["JD Persona"])
    print("✅ JD Persona API router included successfully")
except ImportError as e:
    print(f"⚠️ JD Persona API import failed: {e}")
    print("   This may be due to missing dependencies or DB table conflicts")
except Exception as e:
    print(f"❌ Unexpected error loading JD Persona API: {e}")

# 기본 CompetencyService 테스트 엔드포인트
@app.get("/api/v1/test/competency-service", tags=["Test"])
async def test_competency_service():
    """
    CompetencyService 기본 기능 테스트 (DB 없이)
    """
    try:
        from services.competency_service import CompetencyService
        competency_service = CompetencyService()

        sample_job_competencies = [
            "데이터분석", "문제해결력", "창의적 사고",
            "기술적 이해", "리더십", "커뮤니케이션"
        ]

        return {
            "status": "success",
            "message": "CompetencyService is working",
            "common_competencies": competency_service.COMMON_COMPETENCIES,
            "sample_job_competencies": sample_job_competencies,
            "visualization_data": competency_service.get_competency_visualization_data(
                sample_job_competencies
            )
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/", tags=["Root"])
async def read_root():
    """
    루트 엔드포인트
    """
    return {"message": "JD Persona Test Server is running!"}

@app.get("/health", tags=["Health"])
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "healthy", "service": "JD_Persona_Test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)