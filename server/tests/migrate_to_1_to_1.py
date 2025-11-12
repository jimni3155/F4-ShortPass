# migrate_to_1_to_1.py
"""
데이터베이스 마이그레이션: N:1 → 1:1 구조 전환

실행 방법:
    python migrate_to_1_to_1.py
"""

from sqlalchemy import create_engine, text
from core.config import DATABASE_URL
import sys


def migrate_database():
    """데이터베이스 마이그레이션 실행"""
    engine = create_engine(DATABASE_URL)

    print("=" * 60)
    print("데이터베이스 마이그레이션 시작")
    print("N:1 (여러 회사 : 1명) → 1:1 (1개 회사 : 1명, 순차 페르소나)")
    print("=" * 60)

    try:
        with engine.connect() as conn:
            # 1. interview_sessions 테이블 수정
            print("\n[1/6] interview_sessions 테이블 수정 중...")

            # 기존 job_ids 컬럼 삭제 및 company_id 추가
            conn.execute(text("""
                ALTER TABLE interview_sessions
                DROP COLUMN IF EXISTS job_ids;
            """))
            conn.commit()

            conn.execute(text("""
                ALTER TABLE interview_sessions
                ADD COLUMN IF NOT EXISTS company_id INTEGER REFERENCES companies(id);
            """))
            conn.commit()

            conn.execute(text("""
                ALTER TABLE interview_sessions
                ADD COLUMN IF NOT EXISTS current_persona_index INTEGER DEFAULT 0 NOT NULL;
            """))
            conn.commit()

            # 인덱스 추가
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_interview_sessions_company_id
                ON interview_sessions(company_id);
            """))
            conn.commit()

            print("   ✓ interview_sessions 테이블 수정 완료")

            # 2. persona_instances 테이블 생성
            print("\n[2/6] persona_instances 테이블 생성 중...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS persona_instances (
                    id SERIAL PRIMARY KEY,
                    company_id INTEGER NOT NULL REFERENCES companies(id),
                    persona_template_id INTEGER NOT NULL REFERENCES personas(id),
                    instance_name VARCHAR(100) NOT NULL,
                    custom_weights JSONB,
                    question_tone TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                );
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_persona_instances_company_id
                ON persona_instances(company_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_persona_instances_persona_template_id
                ON persona_instances(persona_template_id);
            """))
            conn.commit()

            print("   ✓ persona_instances 테이블 생성 완료")

            # 3. session_personas 테이블 생성
            print("\n[3/6] session_personas 테이블 생성 중...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS session_personas (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
                    persona_instance_id INTEGER NOT NULL REFERENCES persona_instances(id),
                    "order" INTEGER NOT NULL,
                    role VARCHAR(50) DEFAULT 'primary' NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                );
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_personas_session_id
                ON session_personas(session_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_personas_persona_instance_id
                ON session_personas(persona_instance_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_personas_session_order
                ON session_personas(session_id, "order");
            """))
            conn.commit()

            print("   ✓ session_personas 테이블 생성 완료")

            # 4. session_transcripts 테이블 생성
            print("\n[4/6] session_transcripts 테이블 생성 중...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS session_transcripts (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
                    persona_instance_id INTEGER REFERENCES persona_instances(id),
                    turn INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    meta_json JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                );
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_transcripts_session_id
                ON session_transcripts(session_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_transcripts_persona_instance_id
                ON session_transcripts(persona_instance_id);
            """))
            conn.commit()

            print("   ✓ session_transcripts 테이블 생성 완료")

            # 5. session_scores 테이블 생성
            print("\n[5/6] session_scores 테이블 생성 중...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS session_scores (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
                    persona_instance_id INTEGER NOT NULL REFERENCES persona_instances(id),
                    criterion_key VARCHAR(100) NOT NULL,
                    score DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                );
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_scores_session_id
                ON session_scores(session_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_scores_persona_instance_id
                ON session_scores(persona_instance_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_scores_criterion_key
                ON session_scores(criterion_key);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_scores_session_persona_criterion
                ON session_scores(session_id, persona_instance_id, criterion_key);
            """))
            conn.commit()

            print("   ✓ session_scores 테이블 생성 완료")

            # 6. session_explanations 테이블 생성
            print("\n[6/6] session_explanations 테이블 생성 중...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS session_explanations (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES interview_sessions(id) ON DELETE CASCADE,
                    persona_instance_id INTEGER NOT NULL REFERENCES persona_instances(id),
                    criterion_key VARCHAR(100) NOT NULL,
                    explanation TEXT,
                    log_json JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
                );
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_explanations_session_id
                ON session_explanations(session_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_explanations_persona_instance_id
                ON session_explanations(persona_instance_id);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_explanations_criterion_key
                ON session_explanations(criterion_key);
            """))
            conn.commit()

            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_session_explanations_session_persona_criterion
                ON session_explanations(session_id, persona_instance_id, criterion_key);
            """))
            conn.commit()

            print("   ✓ session_explanations 테이블 생성 완료")

        print("\n" + "=" * 60)
        print("✅ 마이그레이션 성공!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 마이그레이션 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    migrate_database()
