import API_V1 from '../lib/apiConfig';

/**
 * 지원자 ID와 선택된 회사 목록을 기반으로 인터뷰 질문을 준비하도록 서버에 요청합니다.
 * Note: 실제 인터뷰는 WebSocket을 통해 진행됩니다 (ws://localhost:8000/api/v1/ws/interview)
 *
 * @param {string} candidateId - 현재 지원자의 고유 ID.
 * @param {string[]} selectedCompanyIds - 선택된 회사의 ID 배열 (최소 1개, 최대 3개).
 * @returns {Promise<{interviewId: string}>} 준비된 인터뷰 세션의 ID를 포함하는 객체.
 */

export const prepareQuestions = async (candidateId, selectedCompanyIds) => {
    if (!candidateId || selectedCompanyIds.length === 0) {
      throw new Error(
        'Candidate ID and at least one company selection are required.'
      );
    }

    const payload = {
      candidateId: candidateId,
      companyIds: selectedCompanyIds,
    };

    try {
      // TODO: 백엔드에 인터뷰 준비 REST API가 필요하거나, WebSocket으로 직접 연결
      const response = await fetch(`${API_V1}/interviews/prepare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail ||  `Failed to prepare interview. Status: ${response.status}`
        );
      }
      

      // 서버는 생성된 인터뷰 세션 ID를 반환
      return await response.json();
    } catch (error) {
      console.error('Error preparing questions:', error);
      throw error;
    }
  };
  
  /**
   * 특정 인터뷰 세션의 회사별 최종 매칭 점수를 가져옵니다.
   *
   * @param {number} interviewId - 점수를 조회할 인터뷰 세션의 고유 ID.
   * @returns {Promise<Object>} 매칭 결과 객체 (지원자 정보, 회사별 매칭 점수 등).
   */
  export const fetchCandidateCompanyScores = async (interviewId) => {
    if (!interviewId) {
      throw new Error('Interview ID is required to fetch scores.');
    }

    try {
      const response = await fetch(`/api/v1/applicant/interviews/${interviewId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.message ||
            `Failed to fetch company scores. Status: ${response.status}`
        );
      }

      // 서버 응답이 기대하는 배열 형태라고 가정합니다.
      return await response.json();
    } catch (error) {
      console.error('Error fetching company scores:', error);
      throw error;
    }
  };
  