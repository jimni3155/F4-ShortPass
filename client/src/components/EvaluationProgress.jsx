import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

/**
 * 실시간 평가 진행 상황 컴포넌트
 * SSE(Server-Sent Events)를 통해 백엔드에서 진행 상황을 실시간으로 받아 표시
 */
const EvaluationProgress = ({ interviewId, applicantId, jobId, onComplete }) => {
  const navigate = useNavigate();
  const eventSourceRef = useRef(null);

  // 상태
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState(null);
  const [stages, setStages] = useState([
    { id: 0, name: '초기화', status: 'pending', message: '' },
    { id: 1, name: 'Stage 1: 역량별 평가', status: 'pending', message: '' },
    { id: 2, name: 'Stage 2: 통합 분석', status: 'pending', message: '' },
    { id: 3, name: 'Stage 3: 최종 통합', status: 'pending', message: '' },
    { id: 4, name: 'Stage 4: 결과 포맷팅', status: 'pending', message: '' },
  ]);
  const [competencies, setCompetencies] = useState({});
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // 평가 시작
  const startEvaluation = async () => {
    setIsRunning(true);
    setError(null);
    setResult(null);
    setProgress(0);
    setLogs([]);
    setCompetencies({});

    // 단계 초기화
    setStages(prev => prev.map(s => ({ ...s, status: 'pending', message: '' })));

    try {
      // SSE 연결
      const response = await fetch(`${API_BASE}/evaluations/stream/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          interview_id: interviewId,
          applicant_id: applicantId,
          job_id: jobId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            const eventType = line.slice(7);
            continue;
          }

          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              handleSSEEvent(data);
            } catch (e) {
              console.error('SSE 파싱 오류:', e);
            }
          }
        }
      }
    } catch (err) {
      console.error('평가 오류:', err);
      setError(err.message);
      setIsRunning(false);
    }
  };

  // SSE 이벤트 처리
  const handleSSEEvent = (data) => {
    const timestamp = new Date().toLocaleTimeString();

    // progress 이벤트
    if (data.stage !== undefined) {
      setCurrentStage(data.stage);
      setProgress(data.progress || 0);

      // 단계 상태 업데이트
      setStages(prev => prev.map(s => {
        if (s.id === data.stage) {
          return { ...s, status: data.status, message: data.message };
        }
        if (s.id < data.stage && s.status !== 'completed') {
          return { ...s, status: 'completed' };
        }
        return s;
      }));

      // 로그 추가
      addLog(`[Stage ${data.stage}] ${data.message}`, data.status === 'completed' ? 'success' : 'info');
    }

    // 역량 시작
    if (data.competency && data.index) {
      if (data.score !== undefined) {
        // 완료
        setCompetencies(prev => ({
          ...prev,
          [data.competency]: { score: data.score, status: 'completed' }
        }));
        addLog(`  [완료] ${data.competency}: ${data.score}점`, 'success');
      } else {
        // 시작
        setCompetencies(prev => ({
          ...prev,
          [data.competency]: { score: null, status: 'in_progress' }
        }));
        addLog(`  [평가 중] ${data.competency} (${data.index}/${data.total})`, 'info');
      }
    }

    // substep
    if (data.substep) {
      addLog(`    - ${data.message}`, 'info');
    }

    // 완료
    if (data.status === 'completed' && data.final_score !== undefined) {
      setResult(data);
      setIsRunning(false);
      addLog(`평가 완료! 최종 점수: ${data.final_score.toFixed(1)}점`, 'success');

      if (onComplete) {
        onComplete(data);
      }
    }

    // 에러
    if (data.status === 'failed') {
      setError(data.message);
      setIsRunning(false);
      addLog(`오류: ${data.message}`, 'error');
    }
  };

  // 로그 추가
  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev, { timestamp, message, type }]);
  };

  // 결과 페이지로 이동
  const goToResult = () => {
    navigate(`/company/applicants/${jobId}/${applicantId}`);
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* 헤더 */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI 면접 평가</h2>
        <p className="text-gray-600">
          Interview ID: {interviewId} | Applicant ID: {applicantId}
        </p>

        {!isRunning && !result && (
          <button
            onClick={startEvaluation}
            className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            평가 시작
          </button>
        )}
      </div>

      {/* 진행 바 */}
      {(isRunning || result) && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">전체 진행률</span>
            <span className="text-sm font-medium text-blue-600">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {/* 단계별 진행 상황 */}
      {(isRunning || result) && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">진행 단계</h3>

          <div className="space-y-4">
            {stages.map((stage, idx) => (
              <div key={stage.id} className="flex items-start gap-4">
                {/* 아이콘 */}
                <div className={`
                  w-8 h-8 rounded-full flex items-center justify-center shrink-0
                  ${stage.status === 'completed' ? 'bg-green-100 text-green-600' :
                    stage.status === 'in_progress' ? 'bg-blue-100 text-blue-600' :
                    'bg-gray-100 text-gray-400'}
                `}>
                  {stage.status === 'completed' ? (
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : stage.status === 'in_progress' ? (
                    <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                  ) : (
                    <span className="text-sm font-medium">{stage.id}</span>
                  )}
                </div>

                {/* 내용 */}
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`font-medium ${
                      stage.status === 'completed' ? 'text-green-700' :
                      stage.status === 'in_progress' ? 'text-blue-700' :
                      'text-gray-500'
                    }`}>
                      {stage.name}
                    </span>
                    {stage.status === 'in_progress' && (
                      <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
                        진행 중
                      </span>
                    )}
                  </div>
                  {stage.message && (
                    <p className="text-sm text-gray-500 mt-1">{stage.message}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 역량별 점수 (Stage 1 진행 중 또는 완료 시) */}
      {Object.keys(competencies).length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">역량별 평가</h3>

          <div className="grid grid-cols-2 gap-3">
            {Object.entries(competencies).map(([name, data]) => (
              <div
                key={name}
                className={`p-3 rounded-lg border ${
                  data.status === 'completed' ? 'bg-green-50 border-green-200' :
                  'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700 truncate" title={name}>
                    {name.replace(/_/g, ' ')}
                  </span>
                  {data.status === 'completed' ? (
                    <span className="text-lg font-bold text-green-600">{data.score}</span>
                  ) : (
                    <svg className="w-4 h-4 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 실시간 로그 */}
      {logs.length > 0 && (
        <div className="bg-gray-900 rounded-lg shadow-sm p-4 mb-6 max-h-80 overflow-y-auto">
          <h3 className="text-sm font-semibold text-gray-400 mb-3">실행 로그</h3>
          <div className="font-mono text-xs space-y-1">
            {logs.map((log, idx) => (
              <div key={idx} className={`
                ${log.type === 'success' ? 'text-green-400' :
                  log.type === 'error' ? 'text-red-400' :
                  'text-gray-300'}
              `}>
                <span className="text-gray-500">[{log.timestamp}]</span> {log.message}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 결과 요약 */}
      {result && (
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">평가 완료!</h3>
              <p className="text-gray-600">AI 면접 평가가 성공적으로 완료되었습니다.</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">최종 점수</p>
              <p className="text-3xl font-bold text-blue-600">{result.final_score?.toFixed(1)}</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">평균 신뢰도</p>
              <p className="text-3xl font-bold text-gray-700">{(result.avg_confidence * 100)?.toFixed(0)}%</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">신뢰도 레벨</p>
              <p className="text-xl font-bold text-gray-700 capitalize">{result.reliability_level}</p>
            </div>
          </div>

          <button
            onClick={goToResult}
            className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            상세 결과 보기
          </button>
        </div>
      )}

      {/* 에러 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-red-700">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">오류 발생</span>
          </div>
          <p className="mt-2 text-sm text-red-600">{error}</p>
          <button
            onClick={startEvaluation}
            className="mt-3 px-4 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700"
          >
            다시 시도
          </button>
        </div>
      )}
    </div>
  );
};

export default EvaluationProgress;
