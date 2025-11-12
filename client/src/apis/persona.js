// client/src/apis/persona.js
/**
 * 페르소나 관련 API 함수들
 */

import API_V1 from '../lib/apiConfig';

const API_BASE_URL = API_V1;

/**
 * 페르소나 PDF 업로드
 * @param {number} companyId - 회사 ID
 * @param {File} pdfFile - PDF 파일
 * @returns {Promise<Object>} 생성된 페르소나 정보
 */
export const uploadPersonaPdf = async (companyId, pdfFile) => {
  const formData = new FormData();
  formData.append('company_id', companyId);
  formData.append('pdf_file', pdfFile);

  const response = await fetch(`${API_BASE_URL}/personas/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '페르소나 업로드 실패');
  }

  return response.json();
};

/**
 * 페르소나 상세 조회
 * @param {number} personaId - 페르소나 ID
 * @returns {Promise<Object>} 페르소나 정보
 */
export const getPersona = async (personaId) => {
  const response = await fetch(`${API_BASE_URL}/personas/${personaId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '페르소나 조회 실패');
  }

  return response.json();
};

/**
 * 페르소나 질문 목록 조회
 * @param {number} personaId - 페르소나 ID
 * @returns {Promise<Array>} 질문 리스트
 */
export const getPersonaQuestions = async (personaId) => {
  const response = await fetch(`${API_BASE_URL}/personas/${personaId}/questions`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '질문 조회 실패');
  }

  return response.json();
};

/**
 * 회사별 페르소나 목록 조회
 * @param {number} companyId - 회사 ID
 * @returns {Promise<Object>} 페르소나 리스트
 */
export const getPersonasByCompany = async (companyId) => {
  const response = await fetch(`${API_BASE_URL}/personas/company/${companyId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '페르소나 목록 조회 실패');
  }

  return response.json();
};

/**
 * 전체 페르소나 목록 조회
 * @returns {Promise<Object>} 전체 페르소나 리스트
 */
export const getAllPersonas = async () => {
  const response = await fetch(`${API_BASE_URL}/personas/`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '페르소나 목록 조회 실패');
  }

  return response.json();
};

/**
 * 페르소나 삭제
 * @param {number} personaId - 페르소나 ID
 * @returns {Promise<void>}
 */
export const deletePersona = async (personaId) => {
  const response = await fetch(`${API_BASE_URL}/personas/${personaId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '페르소나 삭제 실패');
  }

  return;
};
