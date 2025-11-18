# JD Upload, Processing, and Persona Generation System - Implementation Report

## Executive Summary

The system implements a comprehensive JD (Job Description) processing and persona generation pipeline with RAG capabilities, vector embeddings, competency analysis, and LLM-based persona creation. The architecture spans backend APIs, database models, LLM agents, and frontend components.

---

## 1. JD Upload Flow and Endpoints

### 1.1 Current JD Upload Endpoint
**Location:** `/home/ec2-user/flex/server/api/job.py`

#### Endpoint: `POST /api/v1/jobs/upload`
```
Route: /jobs/upload
Method: POST
Authentication: None (DB Session injected)
Content-Type: multipart/form-data

Parameters:
- pdf_file (File): JD PDF file (max 10MB)
- company_id (Form): Company ID (required)
- title (Form): Job title (required)

Response: JobResponse
{
  "job_id": int,
  "company_id": int,
  "title": str,
  "created_at": str (ISO format),
  "total_chunks": int
}
```

### 1.2 Complete JD Processing Flow
**Location:** `/home/ec2-user/flex/server/services/job_service.py` → `process_jd_pdf()`

**5-Step Processing Pipeline:**

1. **PDF Upload to S3**
   - Uses `S3Service` to store PDF in `jd_pdfs` folder
   - Returns S3 key for future reference

2. **PDF Parsing and Chunking**
   - Uses `JDParser` (chunk_size=1000, chunk_overlap=200)
   - Extracts full text from PDF
   - Splits into semantic chunks with sentence boundary preservation
   - Returns parsed text and chunks

3. **Company Weights Extraction** (NEW - Recently Added)
   - Calls `_extract_company_weights()` using JD text
   - Updates Company table with `category_weights`
   - Stores reasoning in `company_culture_desc`

4. **Embedding Generation**
   - Uses `EmbeddingService` with Bedrock Titan Text Embeddings V2
   - Generates 1024-dimensional vectors for each chunk
   - Batch processing (5 chunks per batch)

5. **Database Persistence**
   - Saves Job record with full text
   - Saves JobChunk records with embeddings
   - Creates indexes for vector similarity search

### 1.3 Job-Related Endpoints

**GET /api/v1/jobs/{job_id}**
- Returns full job details including all chunks
- Response: JobDetailResponse

**POST /api/v1/jobs/search**
- Vector similarity search across job chunks
- Parameters: query (text), top_k (int), job_id (optional)
- Uses cosine distance on embeddings
- Response: List[SearchResult]

**DELETE /api/v1/jobs/{job_id}**
- Deletes job and all associated chunks (CASCADE)
- Response: {message: str}

---

## 2. Database Schema for Jobs and Chunks

### 2.1 Jobs Table
**Location:** `/home/ec2-user/flex/server/models/job.py`

```python
class Job(Base):
    __tablename__ = "jobs"
    
    # Basic Fields
    id: int (PK)
    company_id: int
    title: str(500)
    description: Text  # Full extracted JD text
    
    # RAG Agent Parsing Results
    required_skills: JSON  # List of required tech/skills
    preferred_skills: JSON  # List of preferred tech/skills
    domain_requirements: JSON  # Domain knowledge requirements
    dynamic_evaluation_criteria: JSON  # 5 dynamic evaluation criteria
    competency_weights: JSON  # 6-competency weights
    weights_reasoning: JSON  # Why those weights were assigned
    position_type: str(100)  # backend, frontend, fullstack, devops, etc.
    seniority_level: str(50)  # junior, mid, senior, lead, principal
    main_responsibilities: JSON  # 3-5 key responsibilities
    
    # Timestamps
    created_at: DateTime (auto-set)
    updated_at: DateTime (auto-set)
    
    # Relationships
    chunks: relationship("JobChunk", cascade="all, delete-orphan")
```

### 2.2 JobChunk Table
**Location:** `/home/ec2-user/flex/server/models/job.py`

```python
class JobChunk(Base):
    __tablename__ = "job_chunks"
    
    # Basic Fields
    id: int (PK)
    job_id: int (FK → jobs.id, CASCADE)
    chunk_text: Text
    chunk_index: int  # Order of chunk
    
    # Vector Embedding (pgvector)
    embedding: Vector(1024)  # Amazon Titan Text Embeddings V2
    
    # Timestamp
    created_at: DateTime (auto-set)
    
    # Indexes
    - Index on (job_id, chunk_index)
    - HNSW index for vector similarity search (created manually)
```

### 2.3 Database Schema Migrations
**Location:** `/home/ec2-user/flex/server/docs/schema_updates/`

**004_add_rag_fields_to_jobs.sql:**
- Adds RAG Agent fields to jobs table
- Fields: required_skills, preferred_skills, domain_requirements
- Fields: dynamic_evaluation_criteria, seniority_level, main_responsibilities
- Fields: competency_weights, position_type
- Indexes on position_type and seniority_level

---

## 3. Persona Generation System

### 3.1 Persona Data Models

#### PersonaDB Model
**Location:** `/home/ec2-user/flex/server/models/persona.py` (Dataclass-based)

```python
@dataclass
class Persona:
    persona_id: str  # "interviewer_1"
    company_id: str
    company_name: str
    archetype: ArchetypeEnum  # analytical, supportive, stress_tester
    system_prompt: str  # LLM system prompt
    welcome_message: str  # First greeting
    style_description: str  # For UI display
    focus_keywords: List[str]  # Focus areas
```

#### JDPersona Model
**Location:** `/home/ec2-user/flex/server/models/jd_persona.py`

```python
class JDPersona(Base):
    __tablename__ = "jd_personas"
    
    # Basic Fields
    id: int (PK)
    job_id: int
    company_id: int
    company_name: str(255)
    
    # Extracted Competencies (JSON)
    common_competencies: JSON  # 6 fixed competencies
    job_competencies: JSON  # 6 job-specific competencies
    
    # Core Data
    core_questions: JSON  # 3 company-provided questions
    persona_summary: JSON  # Generated persona info
    analysis_summary: Text
    visualization_config: JSON
    
    # Status
    is_active: bool (default=True)
    created_at: DateTime
    updated_at: DateTime
    
    # Relationships
    questions: relationship("JDPersonaQuestion", cascade="all, delete-orphan")
```

#### JDPersonaQuestion Model
```python
class JDPersonaQuestion(Base):
    __tablename__ = "jd_persona_questions"
    
    id: int (PK)
    persona_id: int (FK → jd_personas.id)
    persona_type: str(100)
    question_text: Text
    question_category: str(50)
    target_competencies: JSON
    created_at: DateTime
    is_active: bool
```

### 3.2 Persona Generation Endpoints

**Location:** `/home/ec2-user/flex/server/api/jd_persona.py`

#### POST /api/v1/jd-persona/upload
- Uploads JD PDF and analyzes competencies
- Calls JobService.process_jd_pdf()
- Calls CompetencyService.analyze_jd_competencies()
- Returns: CompetencyAnalysisResponse

#### POST /api/v1/jd-persona/generate-persona
- Generates personas from JD
- Requires: job_id, company_questions (3 questions)
- Calls JDPersonaService.create_and_save_persona()
- Returns: PersonaResponse

#### GET /api/v1/jd-persona/analysis/{job_id}
- Gets competency analysis for existing job
- Returns: CompetencyAnalysisResponse

#### GET /api/v1/jd-persona/jobs/{job_id}/basic-info
- Gets job basic info
- Returns: {job_id, company_id, title, created_at, total_chunks}

---

## 4. Competency Analysis System

### 4.1 Competency Service
**Location:** `/home/ec2-user/flex/server/services/competency_service.py`

#### Core Competencies (Fixed)
```python
COMMON_COMPETENCIES = [
    "고객지향",
    "도전정신",
    "협동",
    "팀워크",
    "목표지향",
    "책임감"
]
```

#### Main Methods

**analyze_jd_competencies(jd_text: str)**
- Extracts job-specific competencies (6 items)
- Uses LLM with structured prompt
- Returns: {common_competencies, job_competencies, analysis_summary}

**generate_persona_data(jd_text, job_competencies, company_questions)**
- Generates 2 interviewer personas
- Maps competencies to each persona
- Returns: Complete persona JSON with persona_summary

**get_competency_visualization_data(job_competencies)**
- Generates hexagon chart data
- Returns visualization config for frontend

### 4.2 JD Persona Service
**Location:** `/home/ec2-user/flex/server/services/jd_persona_service.py`

**create_and_save_persona()**
- Orchestrates complete persona creation
- Calls CompetencyService for analysis
- Generates visualization data
- Saves JDPersona record to DB
- Returns: Complete persona dict with visualization_data

---

## 5. RAG Agent and Keyword Extraction

### 5.1 RAG Agent
**Location:** `/home/ec2-user/flex/server/ai/agents/rag_agent.py`

#### parse_jd(job_description, job_title)
- Extracts structured JD information
- Uses Claude/Bedrock LLM
- Returns:
  ```python
  {
    "required_skills": List[str],  # Max 10
    "preferred_skills": List[str],  # Max 5
    "domain_requirements": List[str],
    "dynamic_evaluation_criteria": List[str],  # Exactly 5
    "competency_weights": Dict[str, float],  # 6 competencies, sum=1.0
    "position_type": str,  # backend, frontend, fullstack, etc.
    "seniority_level": str,  # junior, mid, senior, lead, principal
    "main_responsibilities": List[str]  # 3-5 items
  }
  ```

#### Competency Weights Structure
```python
competency_weights = {
    "job_expertise": 0.40,        # Job-specific technical skill
    "analytical": 0.15,            # Analytical thinking
    "execution": 0.20,             # Ability to execute
    "relationship": 0.10,          # Team collaboration
    "resilience": 0.05,            # Stress management
    "influence": 0.10              # Leadership/influence
}
```

#### Validation Rules
1. dynamic_evaluation_criteria must be exactly 5 items
2. competency_weights must sum to 1.0
3. required_skills and preferred_skills have no duplicates
4. No speculation - uses explicit JD content only

#### Methods
- `_build_jd_parsing_prompt()` - Constructs the LLM prompt
- `_validate_parsed_data()` - Validates and normalizes output
- `_get_default_weights()` - Fallback weights if parsing fails
- `get_competency_definition()` - Returns competency definitions
- `get_persona_info()` - Retrieves persona from DB

### 5.2 JD Parser
**Location:** `/home/ec2-user/flex/server/ai/parsers/jd_parser.py`

#### parse_pdf(pdf_content: bytes)
- Extracts text from PDF using pdfplumber
- Cleans text (removes extra whitespace)
- Returns full text string

#### split_into_chunks(text, metadata)
- Splits text into semantic chunks
- Preserves sentence boundaries
- Default: chunk_size=1000, chunk_overlap=200
- Returns: List of chunk dicts with chunk_text, chunk_index, metadata

#### parse_and_chunk(pdf_content, metadata)
- Combined method: parse + chunk
- Returns: {full_text, chunks, total_chunks, total_chars}

---

## 6. Frontend Implementation

### 6.1 Job Creation Page
**Location:** `/home/ec2-user/flex/client/src/pages/CompanyInfo.jsx`

#### Form Fields
- Company name (text input)
- Company size (select dropdown)
- JD PDF upload (file input)
- Persona question PDF upload (file input)
- Additional questions (list)
- Blind recruitment toggle

#### Persona Generation Section
- PDF upload component
- "Generate Persona" button
- Status display
- Generated personas list display
- Shows: persona_name, description, archetype, focus_keywords

#### Key Functions
```javascript
handlePersonaUpload()
- Validates company saved first
- Calls uploadPersonaPdf(companyId, personaPdf)
- Displays result status
- Refreshes persona list

handleSave()
- Saves company info
- Sets companyId for persona upload
- Navigates to company result page
```

### 6.2 Client API Functions
**Location:** `/home/ec2-user/flex/client/src/apis/persona.js`

```javascript
uploadPersonaPdf(companyId, pdfFile)
- POST /personas/upload
- FormData with company_id and pdf_file

getPersona(personaId)
- GET /personas/{personaId}

getPersonaQuestions(personaId)
- GET /personas/{personaId}/questions

getPersonasByCompany(companyId)
- GET /personas/company/{companyId}

getAllPersonas()
- GET /personas/

deletePersona(personaId)
- DELETE /personas/{personaId}
```

---

## 7. Persona Question Parser

### 7.1 PersonaQuestionParser
**Location:** `/home/ec2-user/flex/server/ai/parsers/persona_question_parser.py`

#### parse_pdf(pdf_content)
- Extracts text from persona question PDF
- Same as JDParser

#### extract_questions_with_llm(pdf_text, company_name)
- Uses Claude/Bedrock to extract structured questions
- LLM response format:
  ```json
  {
    "persona_info": {
      "persona_name": str,
      "archetype": "analytical|supportive|stress_tester",
      "description": str,
      "focus_areas": List[str]
    },
    "questions": [
      {
        "question_text": str,
        "question_type": "technical|behavioral|situational|cultural",
        "expected_keywords": List[str],
        "evaluation_criteria": List[str],
        "difficulty_level": int (1-5)
      }
    ]
  }
  ```

#### _extract_questions_fallback()
- Regex-based fallback if LLM fails
- Patterns: "1. question", "Q: question", "? question"
- Minimum length: 10 characters

#### parse_persona_questions(pdf_content, company_name)
- Main entry point
- Calls parse_pdf + extract_questions_with_llm
- Returns: {full_text, persona_info, questions}

---

## 8. Evaluation System Integration

### 8.1 Evaluation Service
**Location:** `/home/ec2-user/flex/server/services/evaluation/evaluation_service.py`

#### _build_initial_state()
- Loads interview transcript
- Loads JD with RAG Agent parsing (if not already done)
- Builds EvaluationState for LangGraph
- RAG Agent called if: `not job.required_skills or not job.dynamic_evaluation_criteria`

#### RAG Agent Integration
```python
if not job.required_skills or not job.dynamic_evaluation_criteria:
    parsed_data = await self.rag_agent.parse_jd(
        job_description=job.description,
        job_title=job.title
    )
    
    # Update job with parsed data
    job.required_skills = parsed_data["required_skills"]
    job.preferred_skills = parsed_data["preferred_skills"]
    job.domain_requirements = parsed_data["domain_requirements"]
    job.dynamic_evaluation_criteria = parsed_data["dynamic_evaluation_criteria"]
    job.competency_weights = parsed_data["competency_weights"]
    job.position_type = parsed_data["position_type"]
    job.seniority_level = parsed_data["seniority_level"]
    job.main_responsibilities = parsed_data["main_responsibilities"]
```

### 8.2 Persona Prompts
**Location:** `/home/ec2-user/flex/server/ai/prompts/personas/`

Three persona types:
1. **CTO Persona** (cto_persona_prompt.py) - Technical expertise focus
2. **HR Persona** (hr_persona_prompt.py) - Culture fit focus
3. **Performance Manager Persona** (performance_persona_prompt.py) - Achievement focus

---

## 9. API Endpoints Currently Disabled

**Location:** `/home/ec2-user/flex/server/main.py` (Lines 3-41)

The following routers are commented out:
```python
# app.include_router(job.router, prefix="/api/v1")
# app.include_router(interview_report.router, prefix="/api/v1")
# app.include_router(applicant.router, prefix="/api/v1")
# app.include_router(company.router, prefix="/api/v1")
# app.include_router(persona.router, prefix="/api/v1/personas")
# app.include_router(evaluation.router, prefix="/api/v1")
# app.include_router(jd_persona.router, prefix="/api/v1")
```

Only interview.router is currently active.

---

## 10. Key Files Summary

### Backend Core
- `/home/ec2-user/flex/server/api/job.py` - JD upload/search endpoints
- `/home/ec2-user/flex/server/api/jd_persona.py` - Persona generation endpoints
- `/home/ec2-user/flex/server/services/job_service.py` - JD processing logic
- `/home/ec2-user/flex/server/services/jd_persona_service.py` - Persona management
- `/home/ec2-user/flex/server/services/competency_service.py` - Competency analysis
- `/home/ec2-user/flex/server/ai/agents/rag_agent.py` - JD parsing with LLM
- `/home/ec2-user/flex/server/ai/parsers/jd_parser.py` - PDF parsing
- `/home/ec2-user/flex/server/ai/parsers/persona_question_parser.py` - Question extraction

### Database Models
- `/home/ec2-user/flex/server/models/job.py` - Job and JobChunk models
- `/home/ec2-user/flex/server/models/jd_persona.py` - JDPersona models

### Frontend
- `/home/ec2-user/flex/client/src/pages/CompanyInfo.jsx` - Job/persona creation UI
- `/home/ec2-user/flex/client/src/apis/persona.js` - Persona API client

### Configuration & Migrations
- `/home/ec2-user/flex/server/db/database.py` - Database setup with pgvector
- `/home/ec2-user/flex/server/docs/schema_updates/004_add_rag_fields_to_jobs.sql` - RAG fields

---

## 11. Technology Stack

- **Backend:** FastAPI, SQLAlchemy, pgvector
- **Database:** PostgreSQL with pgvector extension
- **LLM:** AWS Bedrock (Claude models)
- **Embeddings:** Amazon Titan Text Embeddings V2 (1024 dimensions)
- **PDF Processing:** pdfplumber
- **Frontend:** React, JavaScript
- **Graph Processing:** LangGraph (for evaluation agents)

---

## 12. Observations and Notes

1. **RAG Fields Integration:** Job model has comprehensive RAG fields added via migration 004
2. **Vector Search:** pgvector enabled for semantic search across job chunks
3. **Company Weights:** Recently added feature to extract category weights from JD
4. **Persona Count:** System generates 2 personas from one JD + company questions
5. **Competency Mapping:** 6 common competencies (fixed) + 6 job-specific (extracted)
6. **Evaluation Criteria:** Dynamic evaluation criteria (5 items) extracted per JD
7. **Fallback Mechanisms:** Most services have fallback logic if LLM calls fail
8. **Async Processing:** Many services use async/await for LLM calls
9. **APIs Currently Disabled:** Most APIs are commented out in main.py - only interview router active

