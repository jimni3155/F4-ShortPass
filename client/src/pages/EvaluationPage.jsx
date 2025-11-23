import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import EvaluationProgress from '../components/EvaluationProgress';

/**
 * 실시간 평가 진행 페이지
 *
 * URL: /evaluation/:interviewId
 * Query params:
 *   - applicantId: 지원자 ID
 *   - jobId: 직무 ID
 *
 * 예시: /evaluation/101?applicantId=101&jobId=1
 */
const EvaluationPage = () => {
  const { interviewId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const applicantId = searchParams.get('applicantId') || interviewId;
  const jobId = searchParams.get('jobId') || '1';

  const handleComplete = (result) => {
    console.log('평가 완료:', result);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-10">
      <div className="max-w-5xl mx-auto px-4">
        {/* 뒤로가기 */}
        <button
          onClick={() => navigate(-1)}
          className="mb-6 text-gray-500 hover:text-gray-700 text-sm flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          뒤로가기
        </button>

        {/* 메인 컴포넌트 */}
        <EvaluationProgress
          interviewId={parseInt(interviewId)}
          applicantId={parseInt(applicantId)}
          jobId={parseInt(jobId)}
          onComplete={handleComplete}
        />

        {/* 안내 카드 */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">평가 진행 안내</h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-blue-600">1.</span>
              <span><strong>Stage 1:</strong> 10개 역량(공통 5개 + 직무 5개)을 병렬로 AI 평가</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">2.</span>
              <span><strong>Stage 2:</strong> Resume 검증, Confidence 계산, 중복 조정</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">3.</span>
              <span><strong>Stage 3:</strong> 최종 점수 통합 및 종합 심사평 생성</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-blue-600">4.</span>
              <span><strong>Stage 4:</strong> 프론트엔드용 데이터 포맷팅</span>
            </li>
          </ul>
          <p className="mt-4 text-xs text-blue-600">
            전체 평가는 약 3-5분 소요됩니다. 페이지를 이탈하지 마세요.
          </p>
        </div>
      </div>
    </div>
  );
};

export default EvaluationPage;
