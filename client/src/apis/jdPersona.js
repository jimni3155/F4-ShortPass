// client/src/apis/jdPersona.js
/**
 * JD 기반 페르소나 생성 API 함수들
 */

import API_V1 from '../lib/apiConfig';

const API_BASE_URL = API_V1;

/**
 * JD PDF 업로드 및 역량 분석
 * @param {File} pdfFile - JD PDF 파일
 * @param {number} companyId - 회사 ID
 * @param {string} title - 채용 공고 제목
 * @returns {Promise<Object>} 역량 분석 결과
 */
export const uploadJDAndAnalyze = async (pdfFile, companyId, title) => {
  const formData = new FormData();
  formData.append('pdf_file', pdfFile);
  formData.append('company_id', companyId);
  formData.append('title', title);

  const response = await fetch(`${API_BASE_URL}/jd-persona/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'JD 업로드 및 분석 실패');
  }

  return response.json();
};

/**
 * AI 면접관 페르소나 생성
 * @param {number} jobId - Job ID
 * @param {string[]} companyQuestions - 필수 질문 3개
 * @returns {Promise<Object>} 생성된 페르소나 정보
 */
export const generatePersona = async (jobId, companyQuestions) => {
  const response = await fetch(`${API_BASE_URL}/jd-persona/generate-persona`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      job_id: jobId,
      company_questions: companyQuestions,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '페르소나 생성 실패');
  }

  return response.json();
};

/**
 * Job ID로 역량 분석 조회
 * @param {number} jobId - Job ID
 * @returns {Promise<Object>} 역량 분석 결과
 */
export const getCompetencyAnalysis = async (jobId) => {
  const response = await fetch(`${API_BASE_URL}/jd-persona/analysis/${jobId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '역량 분석 조회 실패');
  }

  return response.json();
};

/**
 * Job 기본 정보 조회
 * @param {number} jobId - Job ID
 * @returns {Promise<Object>} Job 기본 정보
 */
export const getJobBasicInfo = async (jobId) => {
  const response = await fetch(`${API_BASE_URL}/jd-persona/jobs/${jobId}/basic-info`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Job 정보 조회 실패');
  }

  return response.json();
};

/**
 * 테스트용 샘플 역량 데이터 조회
 * @returns {Promise<Object>} 샘플 역량 데이터
 */
export const getSampleCompetencies = async () => {
  const response = await fetch(`${API_BASE_URL}/jd-persona/test/sample-competencies`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '샘플 데이터 조회 실패');
  }

  return response.json();
};
