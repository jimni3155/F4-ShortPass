/**
 * API 설정 파일
 *
 * Vite 프록시를 사용하여 개발 환경에서 CORS 문제를 해결합니다.
 * vite.config.js에서 '/api'를 'http://localhost:8000'으로 프록시합니다.
 *
 * 프로덕션 환경에서는 환경 변수를 통해 실제 API URL을 지정할 수 있습니다.
 */

// 개발 환경에서는 Vite 프록시를 사용 (상대 경로)
// 프로덕션 환경에서는 환경 변수에서 읽어옴
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// API v1 엔드포인트
export const API_V1 = `${API_BASE_URL}/api/v1`;

// WebSocket URL (HTTP를 WS로 변환)
export const getWebSocketURL = (path) => {
  if (API_BASE_URL) {
    // 절대 URL이 제공된 경우 (예: http://localhost:8000)
    const wsBaseUrl = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');
    return `${wsBaseUrl}${path}`;
  }
  // 상대 경로인 경우 현재 호스트 사용
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsBaseUrl = `${protocol}//${window.location.host}`;
  return `${wsBaseUrl}${path}`;
};

// 개발 환경 여부 확인
export const isDevelopment = import.meta.env.DEV;

// API 호출 헬퍼 함수
export const apiClient = {
  async get(endpoint, options = {}) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error! Status: ${response.status}`);
    }

    return response.json();
  },

  async post(endpoint, data, options = {}) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error! Status: ${response.status}`);
    }

    return response.json();
  },

  async postFormData(endpoint, formData, options = {}) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'POST',
      body: formData,
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error! Status: ${response.status}`);
    }

    return response.json();
  },

  async put(endpoint, data, options = {}) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      body: JSON.stringify(data),
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error! Status: ${response.status}`);
    }

    return response.json();
  },

  async delete(endpoint, options = {}) {
    const response = await fetch(`${API_V1}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP error! Status: ${response.status}`);
    }

    return response.status === 204 ? null : response.json();
  },
};

export default API_V1;
