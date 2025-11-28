import API_V1 from '../lib/apiConfig';

export const saveCandidate = async (candidateData, portfolioPdfFile) => {
    console.log('Saving candidate with data:', candidateData);
    const formData = new FormData();
  
    // 텍스트 데이터를 FormData에 추가
    // Object.entries를 사용하여 객체의 모든 필드를 반복하여 추가할 수 있습니다.
    Object.entries(candidateData).forEach(([key, value]) => {
      formData.append(key, value);
    });
  
    // 파일 데이터를 FormData에 추가 (필수)
    if (portfolioPdfFile) {
      // 'portfolio'는 백엔드가 파일을 인식하는 필드명과 일치해야 합니다.
      formData.append('portfolio_file', portfolioPdfFile);
    }
  
    try {
      const response = await fetch(`${API_V1}/applicants/`, {
        // 실제 엔드포인트 URL
        method: 'POST',
        // Content-Type은 FormData 사용 시 브라우저가 자동으로 설정합니다.
        body: formData,
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Error response from server:', errorData);
        throw new Error(
          errorData.detail || `HTTP error! Status: ${response.status}`
        );
      }
  
      const responseData = await response.json();
      console.log('Successfully saved candidate:', responseData);
      return responseData;
    } catch (error) {
      console.error('Error saving candidate:', error);
      throw error;
    }
  };