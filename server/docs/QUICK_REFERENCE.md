# JD & Persona System - Quick Reference Guide

## File Locations (Absolute Paths)

### API Endpoints
- `/home/ec2-user/flex/server/api/job.py` - JD upload/search endpoints
- `/home/ec2-user/flex/server/api/jd_persona.py` - Persona generation endpoints

### Services
- `/home/ec2-user/flex/server/services/job_service.py` - JD processing (5-step pipeline)
- `/home/ec2-user/flex/server/services/jd_persona_service.py` - Persona management
- `/home/ec2-user/flex/server/services/competency_service.py` - Competency analysis

### AI/LLM
- `/home/ec2-user/flex/server/ai/agents/rag_agent.py` - JD parsing & skill extraction
- `/home/ec2-user/flex/server/ai/parsers/jd_parser.py` - PDF text extraction & chunking
- `/home/ec2-user/flex/server/ai/parsers/persona_question_parser.py` - Question extraction

### Database Models
- `/home/ec2-user/flex/server/models/job.py` - Job and JobChunk tables
- `/home/ec2-user/flex/server/models/jd_persona.py` - JDPersona tables

### Frontend
- `/home/ec2-user/flex/client/src/pages/CompanyInfo.jsx` - Job/persona UI
- `/home/ec2-user/flex/client/src/apis/persona.js` - Persona API client

### Database & Config
- `/home/ec2-user/flex/server/db/database.py` - PostgreSQL + pgvector setup
- `/home/ec2-user/flex/server/docs/schema_updates/004_add_rag_fields_to_jobs.sql` - RAG fields migration

---

## Key Endpoints

### JD Upload
```
POST /api/v1/jobs/upload
Content-Type: multipart/form-data

Request:
- pdf_file: PDF file
- company_id: int
- title: str

Response:
{
  "job_id": int,
  "company_id": int,
  "title": str,
  "created_at": ISO string,
  "total_chunks": int
}
```

### Competency Analysis
```
POST /api/v1/jd-persona/upload
Content-Type: multipart/form-data

Request:
- pdf_file: JD PDF
- company_id: int
- title: str

Response:
{
  "job_id": int,
  "common_competencies": [...6 fixed],
  "job_competencies": [...6 extracted],
  "analysis_summary": str,
  "visualization_data": {...}
}
```

### Persona Generation
```
POST /api/v1/jd-persona/generate-persona
Content-Type: application/json

Request:
{
  "job_id": int,
  "company_questions": [str, str, str]  ← exactly 3
}

Response:
{
  "job_id": int,
  "company": str,
  "common_competencies": [...6],
  "job_competencies": [...6],
  "core_questions": [...3],
  "persona_summary": [
    {
      "type": str,
      "focus": str,
      "target_competencies": [...],
      "example_question": str
    },
    {...}  ← 2 personas total
  ],
  "created_at": ISO string
}
```

---

## Data Flow Summary

### JD Upload Flow (5 Steps)
```
PDF File
  ↓
[1] Upload to S3
  ↓
[2] Parse PDF & Create Chunks
  ↓
[2-1] Extract Company Weights
  ↓
[3] Create Job Record
  ↓
[4] Generate Embeddings (Titan 1024-dim)
  ↓
[5] Save Chunks with Embeddings
  ↓
Job Object + Chunks in DB
```

### Persona Generation Flow
```
JD Text + Company Questions
  ↓
[1] Analyze Competencies (LLM)
  ├─ 6 common competencies (fixed)
  └─ 6 job-specific competencies (extracted)
  ↓
[2] Generate Persona Data (LLM)
  ├─ 2 personas with different focus
  └─ Each maps to 2-3 competencies
  ↓
[3] Create Visualization Data (Hexagon)
  ↓
[4] Save JDPersona Record
  ↓
Persona Summary Ready for Interview
```

---

## Database Schema Quick View

### Jobs Table (Enhanced with RAG)
```
CREATE TABLE jobs (
  id INT PRIMARY KEY,
  company_id INT,
  title VARCHAR(500),
  description TEXT,
  
  -- RAG Agent Results
  required_skills JSON,
  preferred_skills JSON,
  domain_requirements JSON,
  dynamic_evaluation_criteria JSON,  ← exactly 5
  competency_weights JSON,           ← 6 competencies, sum=1.0
  position_type VARCHAR(100),
  seniority_level VARCHAR(50),
  main_responsibilities JSON,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### JobChunk Table (Vector Search)
```
CREATE TABLE job_chunks (
  id INT PRIMARY KEY,
  job_id INT FOREIGN KEY,
  chunk_text TEXT,
  embedding pgvector(1024),  ← Amazon Titan
  chunk_index INT,
  created_at TIMESTAMP
);
```

### JDPersona Table
```
CREATE TABLE jd_personas (
  id INT PRIMARY KEY,
  job_id INT,
  company_id INT,
  company_name VARCHAR(255),
  
  common_competencies JSON,    ← 6 fixed
  job_competencies JSON,       ← 6 extracted
  core_questions JSON,         ← 3 company questions
  persona_summary JSON,        ← 2 personas
  
  analysis_summary TEXT,
  visualization_config JSON,
  is_active BOOLEAN,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

---

## Competency System

### Fixed Competencies (Always 6)
1. 고객지향 (Customer Orientation)
2. 도전정신 (Challenge Spirit)
3. 협동 (Cooperation)
4. 팀워크 (Teamwork)
5. 목표지향 (Goal Orientation)
6. 책임감 (Sense of Responsibility)

### Job-Specific Competencies (Extracted - Always 6)
Examples:
- 데이터분석, 문제해결력, 커뮤니케이션
- 창의적 사고, 기술적 이해, 리더십

### Competency Weights (Always 6 - Sum to 1.0)
```
job_expertise: 0.30-0.45    (varies by job)
analytical: 0.10-0.20
execution: 0.15-0.25
relationship: 0.05-0.15
resilience: 0.05-0.10
influence: 0.05-0.15
```

---

## LLM Integration Points

### RAG Agent - JD Parsing
- **Model:** Claude (via AWS Bedrock)
- **Temperature:** 0.3 (for structured output)
- **Max Tokens:** 2000
- **Purpose:** Extract required_skills, preferred_skills, dynamic_evaluation_criteria, competency_weights
- **Validation:** Must return exactly 5 criteria, weights sum to 1.0

### Competency Service - Analysis
- **Model:** Claude (via AWS Bedrock)
- **Temperature:** 0.3
- **Max Tokens:** 1000
- **Purpose:** Extract 6 job-specific competencies

### Competency Service - Persona Generation
- **Model:** Claude (via AWS Bedrock)
- **Temperature:** 0.5 (more creative)
- **Max Tokens:** 2000
- **Purpose:** Generate 2 interviewer personas with target competencies

### Persona Question Parser
- **Model:** Claude (via AWS Bedrock)
- **Temperature:** 0.3 (for structured output)
- **Max Tokens:** 4096
- **Purpose:** Extract questions and persona info from PDF

---

## Important Implementation Details

### Chunk Configuration
- **Size:** 1000 characters
- **Overlap:** 200 characters
- **Boundary:** Sentence endings (.!?)

### Embedding Model
- **Model:** Amazon Titan Text Embeddings V2
- **Dimensions:** 1024
- **Used for:** Vector similarity search

### Vector Search
- **Index Type:** HNSW (created manually in PostgreSQL)
- **Distance Metric:** Cosine distance
- **Conversion:** similarity = 1 - distance

### Error Handling
- RAG Agent has fallback default data if LLM fails
- Persona Question Parser has regex-based fallback
- All services gracefully degrade with defaults

### Async Processing
- Most LLM calls are async (await)
- Batch embedding generation (5 chunks/batch)
- S3 operations may vary

---

## Frontend Integration Points

### CompanyInfo.jsx
- Handles JD PDF upload
- Handles Persona question PDF upload
- Displays generated personas
- Calls persona API functions

### persona.js API Functions
```javascript
uploadPersonaPdf(companyId, pdfFile)
getPersona(personaId)
getPersonaQuestions(personaId)
getPersonasByCompany(companyId)
getAllPersonas()
deletePersona(personaId)
```

---

## Disabled Endpoints (In main.py)

Currently only interview.router is active. These are commented out:
```python
# app.include_router(job.router, prefix="/api/v1")
# app.include_router(jd_persona.router, prefix="/api/v1")
# app.include_router(evaluation.router, prefix="/api/v1")
# app.include_router(persona.router, prefix="/api/v1/personas")
# app.include_router(company.router, prefix="/api/v1")
# app.include_router(applicant.router, prefix="/api/v1")
# app.include_router(interview_report.router, prefix="/api/v1")
```

To activate: Uncomment the routers in `/home/ec2-user/flex/server/main.py`

---

## Testing Endpoints (Postman/cURL)

### Upload JD
```bash
curl -X POST http://localhost:8000/api/v1/jobs/upload \
  -F "pdf_file=@sample.pdf" \
  -F "company_id=1" \
  -F "title=Backend Developer"
```

### Generate Persona
```bash
curl -X POST http://localhost:8000/api/v1/jd-persona/generate-persona \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1,
    "company_questions": [
      "당사에서의 성장 기회는 무엇이라고 생각하십니까?",
      "팀과의 협업 경험을 설명해주세요.",
      "가장 어려웠던 프로젝트는 무엇이었나요?"
    ]
  }'
```

### Search Similar Chunks
```bash
curl -X POST http://localhost:8000/api/v1/jobs/search \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=Python%20experience&top_k=5&job_id=1"
```

---

## Common Issues & Solutions

### Issue: API endpoints not responding
**Solution:** Check if routers are uncommented in main.py

### Issue: Embedding generation fails
**Solution:** Verify AWS Bedrock access and API keys in config

### Issue: LLM returns invalid JSON
**Solution:** Service has fallback logic - check logs for error details

### Issue: Vector search returns no results
**Solution:** Ensure HNSW index is created and embeddings exist in DB

### Issue: Persona generation missing fields
**Solution:** Verify JD has been parsed with RAG Agent first

---

## Documentation Files

1. **JD_PERSONA_IMPLEMENTATION_REPORT.md** (18KB)
   - Complete system architecture
   - All endpoints documented
   - Database schema details
   - Service descriptions

2. **JD_PERSONA_CODE_SNIPPETS.md** (28KB)
   - Complete code examples
   - Flow diagrams
   - Validation logic
   - Error handling patterns

3. **QUICK_REFERENCE.md** (this file)
   - Quick lookup guide
   - File locations
   - Common tasks
   - Testing commands

---

## Next Steps for Development

1. Uncomment routers in main.py to activate APIs
2. Test JD upload with sample PDFs
3. Implement frontend API calls
4. Add persona selection UI
5. Integrate with interview session
6. Test with real JD documents

