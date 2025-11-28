# JD and Persona System - Code Snippets and Architecture

## Part 1: JD Upload Flow - Code Walkthrough

### 1.1 Frontend - Initiate JD Upload
```javascript
// client/src/pages/CompanyInfo.jsx
const handleSave = async () => {
    setLoading(true);
    try {
        // Save company info
        // TODO: implement saveCompany function
        const tempCompanyId = 1;
        setCompanyId(tempCompanyId);
        
        // Navigate to company result page
        navigate(`/company/result/${tempCompanyId}`);
    } catch (err) {
        alert('저장 중 오류가 발생했습니다.');
    } finally {
        setLoading(false);
    }
};
```

### 1.2 Backend - API Endpoint
```python
# server/api/job.py
@router.post("/upload", response_model=JobResponse)
async def upload_jd_pdf(
    pdf_file: UploadFile = File(..., description="JD PDF 파일"),
    company_id: int = Form(..., description="회사 ID"),
    title: str = Form(..., description="채용 공고 제목"),
    db: Session = Depends(get_db)
):
    # Validate PDF
    if not pdf_file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Check file size (10MB max)
    pdf_content = await pdf_file.read()
    max_size = 10 * 1024 * 1024
    if len(pdf_content) > max_size:
        raise HTTPException(status_code=400, detail=f"File size exceeds {max_size / (1024*1024)}MB")
    
    # Process with JobService
    try:
        job_service = JobService()
        job = await job_service.process_jd_pdf(
            db=db,
            pdf_content=pdf_content,
            file_name=pdf_file.filename,
            company_id=company_id,
            title=title
        )
        
        return JobResponse(
            job_id=job.id,
            company_id=job.company_id,
            title=job.title,
            created_at=job.created_at.isoformat(),
            total_chunks=len(job.chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process JD PDF: {str(e)}")
```

### 1.3 Service - Main Processing Pipeline
```python
# server/services/job_service.py
async def process_jd_pdf(
    self,
    db: Session,
    pdf_content: bytes,
    file_name: str,
    company_id: int,
    title: str
) -> Job:
    try:
        print(f"\n{'='*60}")
        print(f"Starting JD PDF processing: {file_name}")
        print(f"{'='*60}")

        # Step 1: Upload to S3
        print("\n[Step 1/5] Uploading PDF to S3...")
        s3_key = self.s3_service.upload_file(
            file_content=pdf_content,
            file_name=file_name,
            folder="jd_pdfs"
        )

        # Step 2: Parse PDF and create chunks
        print("\n[Step 2/5] Parsing PDF and creating chunks...")
        parsed_result = self.jd_parser.parse_and_chunk(
            pdf_content=pdf_content,
            metadata={
                "company_id": company_id,
                "s3_key": s3_key,
                "file_name": file_name
            }
        )

        full_text = parsed_result["full_text"]
        chunks = parsed_result["chunks"]

        # Step 2-1: Extract company weights (NEW)
        print("\n[Step 2-1/6] Extracting company weights from JD...")
        weights_data = await self._extract_company_weights(full_text)

        if weights_data and "weights" in weights_data and Company:
            try:
                company = db.query(Company).filter(Company.id == company_id).first()
                if company:
                    company.category_weights = weights_data["weights"]
                    if not company.company_culture_desc and "reasoning" in weights_data:
                        company.company_culture_desc = str(weights_data.get("reasoning", {}))
                    db.flush()
                    print(f"  ✓ Company weights updated: {weights_data['weights']}")
            except Exception as e:
                print(f"  ⚠ Failed to update company weights: {e}")

        # Step 3: Create Job record
        print("\n[Step 3/5] Creating Job record...")
        job = Job(
            company_id=company_id,
            title=title,
            description=full_text
        )
        db.add(job)
        db.flush()  # Generate ID
        print(f"  - Job created with ID: {job.id}")

        # Step 4: Generate embeddings
        print("\n[Step 4/5] Generating embeddings for chunks...")
        chunk_texts = [chunk["chunk_text"] for chunk in chunks]
        embeddings = self.embedding_service.generate_embeddings_batch(
            texts=chunk_texts,
            batch_size=5
        )

        # Step 5: Save chunks
        print("\n[Step 5/5] Saving chunks to database...")
        created_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            if embedding is None:
                print(f"  ⚠ Skipping chunk {i} (embedding failed)")
                continue

            job_chunk = JobChunk(
                job_id=job.id,
                chunk_text=chunk["chunk_text"],
                embedding=embedding,
                chunk_index=chunk["chunk_index"]
            )
            db.add(job_chunk)
            created_chunks.append(job_chunk)

        db.commit()
        db.refresh(job)

        print(f"\n{'='*60}")
        print(f"✓ JD Processing completed successfully!")
        print(f"  - Job ID: {job.id}")
        print(f"  - Chunks saved: {len(created_chunks)}")
        print(f"  - S3 Key: {s3_key}")
        print(f"{'='*60}\n")

        return job

    except Exception as e:
        db.rollback()
        print(f"\n✗ JD Processing failed: {e}")
        raise Exception(f"Failed to process JD PDF: {str(e)}")
```

---

## Part 2: RAG Agent - JD Parsing

### 2.1 RAG Agent Parse Flow
```python
# server/ai/agents/rag_agent.py
async def parse_jd(
    self,
    job_description: str,
    job_title: str
) -> Dict[str, Any]:
    """
    Extract structured information from JD
    """
    prompt = self._build_jd_parsing_prompt(job_description, job_title)

    try:
        response = await self.llm_client.ainvoke(prompt)

        # Parse JSON response
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()

        parsed_data = json.loads(response_text)

        # Validate and return
        return self._validate_parsed_data(parsed_data)

    except json.JSONDecodeError as e:
        print(f"RAG Agent: JSON parsing failed - {e}")
        return self._get_default_parsed_data()
    except Exception as e:
        print(f"RAG Agent: JD parsing failed - {e}")
        return self._get_default_parsed_data()
```

### 2.2 RAG Agent Prompt Structure
```python
# server/ai/agents/rag_agent.py
def _build_jd_parsing_prompt(self, job_description: str, job_title: str) -> str:
    return f"""당신은 채용공고를 분석하는 전문가입니다.
아래 채용공고에서 면접 평가에 필요한 정보를 추출하세요.

<채용공고>
직무명: {job_title}

{job_description}
</채용공고>

<추출_항목>
1. **필수 기술 (required_skills)**
   - 공고에서 "필수", "반드시", "required" 등으로 명시된 기술
   - 최대 10개

2. **우대 기술 (preferred_skills)**
   - 공고에서 "우대", "선호", "preferred" 등으로 명시된 기술
   - 최대 5개

3. **도메인 요구사항 (domain_requirements)**
   - 특정 산업/도메인 지식 요구사항

4. **동적 평가 기준 (dynamic_evaluation_criteria)**
   - 이 직무에서 가장 중요한 5개 평가 항목
   - 반드시 5개 (더 많거나 적으면 안 됨)

5. **역량별 가중치 (competency_weights)**
   - 6개 역량의 중요도를 0-1 사이 값으로 (합계 1.0)
   - job_expertise: 직무 전문성
   - analytical: 분석적 사고
   - execution: 실행력
   - relationship: 관계 형성
   - resilience: 회복탄력성
   - influence: 영향력

6. **포지션 타입 (position_type)**
   - 직무 분류: backend, frontend, fullstack, devops, data, pm, designer 등

7. **시니어리티 레벨 (seniority_level)**
   - junior, mid, senior, lead, principal 중 하나

8. **주요 업무 (main_responsibilities)**
   - 핵심 업무 3-5개
</추출_항목>

<출력_형식>
오직 유효한 JSON만 반환하세요.

{{
  "required_skills": ["Python", "FastAPI", "PostgreSQL", ...],
  "preferred_skills": ["Kubernetes", "GraphQL", ...],
  "domain_requirements": ["이커머스", ...],
  "dynamic_evaluation_criteria": [
    "Python 숙련도",
    "AWS 인프라 운영",
    "컨테이너 오케스트레이션",
    "이커머스 도메인 지식",
    "실시간 문제해결 능력"
  ],
  "competency_weights": {{
    "job_expertise": 0.40,
    "analytical": 0.15,
    "execution": 0.20,
    "relationship": 0.10,
    "resilience": 0.05,
    "influence": 0.10
  }},
  "position_type": "backend",
  "seniority_level": "senior",
  "main_responsibilities": [...]
}}
</출력_형식>

<중요_규칙>
1. dynamic_evaluation_criteria는 반드시 정확히 5개
2. competency_weights의 합은 반드시 1.0
3. required_skills와 preferred_skills는 중복 없이
4. 공고에 없는 내용은 추측하지 말고 빈 리스트/기본값
</중요_규칙>

위 형식에 맞춰 JSON만 반환하세요.
"""
```

### 2.3 Validation Logic
```python
# server/ai/agents/rag_agent.py
def _validate_parsed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize parsed data"""

    validated = {
        "required_skills": data.get("required_skills", []),
        "preferred_skills": data.get("preferred_skills", []),
        "domain_requirements": data.get("domain_requirements", []),
        "dynamic_evaluation_criteria": data.get("dynamic_evaluation_criteria", []),
        "competency_weights": data.get("competency_weights", {}),
        "position_type": data.get("position_type", "unknown"),
        "seniority_level": data.get("seniority_level", "mid"),
        "main_responsibilities": data.get("main_responsibilities", [])
    }

    # Validate dynamic_evaluation_criteria (exactly 5)
    criteria = validated["dynamic_evaluation_criteria"]
    if len(criteria) < 5:
        # Add defaults if missing
        default_criteria = [
            "기술 전문성",
            "문제 해결 능력",
            "커뮤니케이션 스킬",
            "팀워크",
            "성장 가능성"
        ]
        while len(criteria) < 5:
            criteria.append(default_criteria[len(criteria)])
    else:
        criteria = criteria[:5]  # Use only top 5

    # Validate competency_weights (sum to 1.0)
    weights = validated["competency_weights"]
    required_keys = ["job_expertise", "analytical", "execution", 
                     "relationship", "resilience", "influence"]

    if not all(key in weights for key in required_keys):
        # Use defaults
        validated["competency_weights"] = self._get_default_weights()
    else:
        # Normalize if sum != 1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            validated["competency_weights"] = {
                key: val / total for key, val in weights.items()
            }

    return validated
```

---

## Part 3: Persona Generation Flow

### 3.1 Competency Service - Persona Generation
```python
# server/services/competency_service.py
async def generate_persona_data(
    self,
    jd_text: str,
    job_competencies: List[str],
    company_questions: List[str]
) -> Dict[str, Any]:
    """
    Generate persona data from JD and competencies
    """
    try:
        prompt = self._build_persona_generation_prompt(
            jd_text, job_competencies, company_questions
        )

        response = await self.llm_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=2000
        )

        result = self._parse_persona_response(response)

        # Add core competencies and questions
        result["common_competencies"] = self.COMMON_COMPETENCIES
        result["job_competencies"] = job_competencies
        result["core_questions"] = company_questions

        return result

    except Exception as e:
        print(f"Error generating persona: {e}")
        return self._get_default_persona_data(job_competencies, company_questions)
```

### 3.2 Persona Prompt
```python
# server/services/competency_service.py
def _build_persona_generation_prompt(
    self,
    jd_text: str,
    job_competencies: List[str],
    company_questions: List[str]
) -> str:
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(company_questions)])
    competencies_text = ", ".join(job_competencies)

    return f"""
다음 정보를 바탕으로 면접관 페르소나 2개를 생성해주세요.

<채용공고>
{jd_text}
</채용공고>

<직무 역량>
{competencies_text}
</직무 역량>

<기업 필수 질문>
{questions_text}
</기업 필수 질문>

요구사항:
1. 서로 다른 평가 초점을 가진 2개의 면접관 페르소나 생성
2. 각 페르소나는 직무 역량 중 2-3개를 중점적으로 평가
3. 실제 면접에서 사용할 수 있는 구체적인 예시 질문 포함

응답 형식 (JSON):
{{
  "company": "회사명 추출",
  "persona_summary": [
    {{
      "type": "논리형 면접관",
      "focus": "문제해결력과 분석적 사고를 중점 평가",
      "target_competencies": ["문제해결력", "분석적 사고"],
      "example_question": "프로젝트에서 예상치 못한 문제를 어떻게 해결했나요?"
    }},
    {{
      "type": "커뮤니케이션형 면접관",
      "focus": "협업 및 소통 능력 평가",
      "target_competencies": ["커뮤니케이션", "리더십"],
      "example_question": "의견 충돌이 있었을 때, 어떻게 조율했나요?"
    }}
  ]
}}

반드시 JSON 형식으로만 응답해주세요.
"""
```

### 3.3 JD Persona Service - Complete Flow
```python
# server/services/jd_persona_service.py
async def create_and_save_persona(
    self,
    db: Session,
    job_id: int,
    company_id: int,
    jd_text: str,
    company_questions: List[str]
) -> Dict[str, Any]:
    """
    Complete persona creation and saving flow
    """
    try:
        print(f"🎭 Starting persona creation for Job {job_id}")

        # Step 1: Analyze competencies
        competency_data = await self.competency_service.analyze_jd_competencies(jd_text)
        print(f" Extracted competencies: {len(competency_data['job_competencies'])} job-specific")

        # Step 2: Generate persona data
        persona_data = await self.competency_service.generate_persona_data(
            jd_text=jd_text,
            job_competencies=competency_data["job_competencies"],
            company_questions=company_questions
        )

        # Step 3: Create visualization data
        visualization_data = self.competency_service.get_competency_visualization_data(
            job_competencies=competency_data["job_competencies"]
        )

        # Step 4: Merge all data
        complete_persona_data = {
            **persona_data,
            "analysis_summary": competency_data.get("analysis_summary", "")
        }

        # Step 5: Save to DB
        jd_persona = JDPersona.create_from_generation_result(
            job_id=job_id,
            company_id=company_id,
            generation_result=complete_persona_data,
            visualization_data=visualization_data
        )

        db.add(jd_persona)
        db.commit()
        db.refresh(jd_persona)

        print(f"✅ Persona saved to DB with ID: {jd_persona.id}")

        # Step 6: Return complete result
        result = jd_persona.to_dict()
        result["visualization_data"] = visualization_data

        return result

    except Exception as e:
        db.rollback()
        print(f"❌ Failed to create persona: {e}")
        raise Exception(f"Failed to create persona: {str(e)}")
```

---

## Part 4: Database Schema Visualization

### 4.1 Database Tables Relationship
```
┌─────────────────────────────────────┐
│          jobs (채용공고)             │
├─────────────────────────────────────┤
│ id (PK)                             │
│ company_id                          │
│ title                               │
│ description (full JD text)          │
│                                     │
│ RAG Agent Fields:                   │
│ ├─ required_skills (JSON)           │
│ ├─ preferred_skills (JSON)          │
│ ├─ domain_requirements (JSON)       │
│ ├─ dynamic_evaluation_criteria (J)  │
│ ├─ competency_weights (JSON)        │
│ ├─ weights_reasoning (JSON)         │
│ ├─ position_type (VARCHAR)          │
│ ├─ seniority_level (VARCHAR)        │
│ └─ main_responsibilities (JSON)     │
│                                     │
│ created_at, updated_at              │
└────────────┬──────────────────────────┘
             │ 1:N
             │
┌────────────▼──────────────────────────┐
│       job_chunks (청크)               │
├─────────────────────────────────────┤
│ id (PK)                             │
│ job_id (FK → jobs.id) CASCADE       │
│ chunk_text (TEXT)                   │
│ embedding (Vector(1024))  ← pgvector│
│ chunk_index (INTEGER)               │
│ created_at                          │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│      jd_personas (페르소나)          │
├─────────────────────────────────────┤
│ id (PK)                             │
│ job_id                              │
│ company_id                          │
│ company_name                        │
│                                     │
│ common_competencies (JSON)  ← 6 fixed
│ job_competencies (JSON)     ← 6 extracted
│ core_questions (JSON)       ← 3 company Q
│ persona_summary (JSON)      ← 2 personas
│                                     │
│ analysis_summary (TEXT)             │
│ visualization_config (JSON)         │
│ is_active (BOOLEAN)                 │
│ created_at, updated_at              │
└────────────┬──────────────────────────┘
             │ 1:N
             │
┌────────────▼──────────────────────────┐
│   jd_persona_questions               │
├─────────────────────────────────────┤
│ id (PK)                             │
│ persona_id (FK → jd_personas.id)    │
│ persona_type                        │
│ question_text                       │
│ question_category                   │
│ target_competencies (JSON)          │
│ is_active                           │
└─────────────────────────────────────┘
```

---

## Part 5: Competency Mapping

### 5.1 Common Competencies (Fixed - 6 items)
```python
COMMON_COMPETENCIES = [
    "고객지향",      # Customer orientation
    "도전정신",      # Challenge spirit
    "협동",          # Cooperation
    "팀워크",        # Teamwork
    "목표지향",      # Goal orientation
    "책임감"         # Sense of responsibility
]
```

### 5.2 Job-Specific Competencies (Extracted per JD - 6 items)
Example from Backend Developer JD:
```json
{
  "job_competencies": [
    "데이터분석",
    "문제해결력",
    "커뮤니케이션",
    "창의적 사고",
    "기술적 이해",
    "리더십"
  ]
}
```

### 5.3 Competency Weights (6 competencies total)
```python
{
  "job_expertise": 0.40,        # 40% - Job-specific technical skills
  "analytical": 0.15,           # 15% - Analytical thinking
  "execution": 0.20,            # 20% - Execution ability
  "relationship": 0.10,         # 10% - Team collaboration
  "resilience": 0.05,           # 5%  - Stress management
  "influence": 0.10              # 10% - Leadership/influence
}
```

### 5.4 Persona-to-Competency Mapping
```json
{
  "persona_summary": [
    {
      "type": "논리형 면접관 (Analytical)",
      "focus": "문제해결력과 분석적 사고를 중점 평가",
      "target_competencies": [
        "분석적 사고",      ← From job_competencies
        "문제해결력"        ← From job_competencies
      ],
      "example_question": "프로젝트에서 예상치 못한 문제를 어떻게 해결했나요?"
    },
    {
      "type": "커뮤니케이션형 면접관 (Collaborative)",
      "focus": "협업 및 소통 능력 평가",
      "target_competencies": [
        "커뮤니케이션",      ← From job_competencies
        "팀워크"             ← From common_competencies
      ],
      "example_question": "의견 충돌이 있었을 때, 어떻게 조율했나요?"
    }
  ]
}
```

---

## Part 6: Vector Search with pgvector

### 6.1 Embedding Generation
```python
# Uses Amazon Titan Text Embeddings V2
# Output: 1024-dimensional vector

chunk_text = "Backend 개발자 필수 요구사항: Python, FastAPI, PostgreSQL..."
embedding = [0.0234, -0.0156, ..., 0.0891]  # 1024 dimensions
```

### 6.2 Vector Similarity Search
```python
# server/services/job_service.py
def search_similar_chunks(
    self,
    db: Session,
    query_text: str,
    top_k: int = 5,
    job_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    from pgvector.sqlalchemy import cosine_distance

    # Generate query embedding
    query_embedding = self.embedding_service.generate_embedding(query_text)

    # Vector similarity search
    query = db.query(
        JobChunk.id,
        JobChunk.job_id,
        JobChunk.chunk_text,
        JobChunk.chunk_index,
        cosine_distance(JobChunk.embedding, query_embedding).label("distance")
    )

    if job_id:
        query = query.filter(JobChunk.job_id == job_id)

    results = query.order_by("distance").limit(top_k).all()

    return [
        {
            "chunk_id": r.id,
            "job_id": r.job_id,
            "chunk_text": r.chunk_text,
            "chunk_index": r.chunk_index,
            "similarity": 1 - r.distance  # Convert distance to similarity
        }
        for r in results
    ]
```

### 6.3 Query Example
```
Query: "Python과 FastAPI 경험"
↓
Generate embedding (1024 dims)
↓
Search job_chunks table using cosine_distance
↓
Return top 5 most similar chunks with similarity scores
```

---

## Part 7: Error Handling and Fallbacks

### 7.1 RAG Agent Fallback
```python
def _get_default_parsed_data(self) -> Dict[str, Any]:
    """Fallback data if RAG Agent fails"""
    return {
        "required_skills": [],
        "preferred_skills": [],
        "domain_requirements": [],
        "dynamic_evaluation_criteria": [
            "기술 전문성",
            "문제 해결 능력",
            "커뮤니케이션 스킬",
            "팀워크",
            "성장 가능성"
        ],
        "competency_weights": {
            "job_expertise": 0.30,
            "analytical": 0.15,
            "execution": 0.20,
            "relationship": 0.15,
            "resilience": 0.10,
            "influence": 0.10,
        },
        "position_type": "unknown",
        "seniority_level": "mid",
        "main_responsibilities": []
    }
```

### 7.2 Persona Question Parser Fallback
```python
def _extract_questions_fallback(self, pdf_text: str, company_name: str) -> Dict[str, Any]:
    """Regex-based fallback if LLM fails"""
    
    # Try regex patterns
    question_patterns = [
        r'^\d+\.\s+(.+?)(?=\n\d+\.|\Z)',  # "1. Question"
        r'^Q\d*[:)]\s+(.+?)(?=\nQ\d*[:)]|\Z)',  # "Q: Question"
        r'^\?\s+(.+?)(?=\n\?|\Z)',  # "? Question"
    ]
    
    questions = []
    for pattern in question_patterns:
        matches = re.finditer(pattern, pdf_text, re.MULTILINE | re.DOTALL)
        for match in matches:
            question_text = match.group(1).strip()
            if len(question_text) > 10:  # Filter short texts
                questions.append({
                    "question_text": question_text,
                    "question_type": "general",
                    "expected_keywords": [],
                    "evaluation_criteria": ["답변의 명확성", "논리적 구조"],
                    "difficulty_level": 3
                })
    
    # If no questions found, create default
    if not questions:
        questions.append({
            "question_text": f"{company_name}에서 요구하는 역량에 대해 설명해주세요",
            "question_type": "general",
            "expected_keywords": [],
            "evaluation_criteria": ["답변의 명확성", "경험의 구체성"],
            "difficulty_level": 3
        })
    
    return {
        "persona_info": {
            "persona_name": f"{company_name} 면접관",
            "archetype": "analytical",
            "description": f"{company_name}의 채용 기준을 평가하는 면접관",
            "focus_areas": ["역량 평가"]
        },
        "questions": questions
    }
```

---

## Part 8: API Integration Points

### 8.1 JD Upload Flow Sequence
```
1. Frontend (CompanyInfo.jsx)
   └─> handleSave()
       └─> POST /api/v1/jobs/upload (if job.pdf provided)

2. Backend (api/job.py)
   └─> upload_jd_pdf()
       └─> JobService.process_jd_pdf()

3. Job Service (services/job_service.py)
   └─> Step 1: S3Service.upload_file()
   └─> Step 2: JDParser.parse_and_chunk()
   └─> Step 2-1: _extract_company_weights()
   └─> Step 3: Create Job DB record
   └─> Step 4: EmbeddingService.generate_embeddings_batch()
   └─> Step 5: Create JobChunk DB records
   └─> Return Job with chunks

4. Response back to Frontend
   └─> JobResponse {job_id, company_id, title, created_at, total_chunks}
```

### 8.2 Persona Generation Flow Sequence
```
1. Frontend (CompanyInfo.jsx)
   └─> handlePersonaUpload()
       └─> POST /api/v1/jd-persona/upload
           └─> (creates Job via JobService)
           └─> CompetencyService.analyze_jd_competencies()

2. Competency Analysis (services/competency_service.py)
   └─> analyze_jd_competencies()
       └─> LLM call: extract 6 job-specific competencies

3. Persona Generation (api/jd_persona.py)
   └─> POST /api/v1/jd-persona/generate-persona
       └─> Request: {job_id, company_questions (3 items)}

4. JD Persona Service (services/jd_persona_service.py)
   └─> create_and_save_persona()
       └─> CompetencyService.analyze_jd_competencies()
       └─> CompetencyService.generate_persona_data()
           └─> LLM call: generate 2 personas
       └─> get_competency_visualization_data()
       └─> JDPersona.create_from_generation_result()
       └─> Save to DB
       └─> Return complete persona object

5. Response to Frontend
   └─> PersonaResponse {job_id, company, competencies, personas, created_at}
```

