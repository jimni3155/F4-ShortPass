import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiClient } from '@lib/apiConfig';
import Badge from '@components/Badge';
import { CompetencyDetailModal } from '@components/CompetencyDetailModal';
import Button from '@components/Button';
import ResumeVerificationModal from '@components/ResumeVerificationModal';

// 역량 이름 한글 매핑
const COMPETENCY_NAMES = {
  problem_solving: '문제해결력',
  organizational_fit: '조직적응력',
  growth_potential: '성장잠재력',
  interpersonal_skill: '대인관계',
  achievement_motivation: '성취동기',
  customer_journey_marketing: '고객여정 마케팅',
  md_data_analysis: '데이터 분석',
  seasonal_strategy_kpi: '시즌전략 KPI',
  stakeholder_collaboration: '이해관계자 협업',
  value_chain_optimization: '가치사슬 최적화',
};

// Stage 정보
const STAGES = [
  { id: 1, name: 'Stage 1', title: '역량별 병렬 평가', desc: '10개 CompetencyAgent 동시 실행' },
  { id: 2, name: 'Stage 2', title: '통합 및 검증', desc: 'Resume 검증, 신뢰도 계산' },
  { id: 3, name: 'Stage 3', title: '최종 결과 생성', desc: '점수 통합 및 분석' },
  { id: 4, name: 'Stage 4', title: '프레젠테이션', desc: '프론트엔드 포맷 생성' },
];

const AgentLogs = () => {
  const { evaluationId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [selectedStage, setSelectedStage] = useState(1);
  const [selectedCompetency, setSelectedCompetency] = useState(null);
  const [recentEvaluations, setRecentEvaluations] = useState([]);


  useEffect(() => {
    if (!evaluationId) {
      loadRecentEvaluations();
    }
  }, [evaluationId]);

  useEffect(() => {
    if (evaluationId) {
      loadAgentLogs();
    }
  }, [evaluationId]);

  const loadRecentEvaluations = async () => {
    try {
      setLoading(true);
      const result = await apiClient.get('/agent-logs/list/recent?limit=20');
      setRecentEvaluations(result.evaluations || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadAgentLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await apiClient.get(`/agent-logs/${evaluationId}`);
      setData(result);
      if (result.stage1_evidence) {
        const firstCompetency = Object.keys(result.stage1_evidence)[0];
        setSelectedCompetency(firstCompetency);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 평가 목록 화면
  if (!evaluationId) {
    return (
      <div className="min-h-screen">
        <div className="container mx-auto px-12 py-8 max-w-[1400px]">
          <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-200">
            <div>
              <h1 className="text-2xl font-bold text-blue">MAS Agent Logs</h1>
              <p className="text-gray-500 text-sm mt-1">멀티에이전트 평가 과정 상세 분석</p>
            </div>
          </div>

          {loading ? (
            <div className="text-center py-20">
              <div className="animate-spin w-8 h-8 border-2 border-blue border-t-transparent rounded-full mx-auto mb-4" />
              <p className="text-gray-500">로딩 중...</p>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-600">{error}</p>
            </div>
          ) : (
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">최근 평가 목록</h2>
              <div className="space-y-3">
                {recentEvaluations.map((ev) => (
                  <div
                    key={ev.evaluation_id}
                    onClick={() => navigate(`/agent-logs/${ev.evaluation_id}`)}
                    className="bg-white border border-gray-200 hover:border-blue hover:shadow-md rounded-lg p-5 cursor-pointer transition-all"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-3">
                          <span className="text-lg font-semibold text-gray-900">
                            {ev.applicant_name || `지원자 ${ev.applicant_id}`}
                          </span>
                          <Badge classname="text-xs bg-gray-100 text-gray-600 px-2">
                            #{ev.evaluation_id}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">
                          {ev.created_at && new Date(ev.created_at).toLocaleString('ko-KR')}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-blue">
                          {ev.match_score?.toFixed(1)}점
                        </div>
                        <div className="text-sm text-gray-500">
                          신뢰도 {(ev.confidence_score * 100)?.toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {recentEvaluations.length === 0 && (
                  <div className="text-center py-16 text-gray-400">
                    평가 기록이 없습니다.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // 로딩 상태
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-10 h-10 border-3 border-blue border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-600">에이전트 로그 로딩 중...</p>
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div className="min-h-screen">
        <div className="container mx-auto px-12 py-8 max-w-[1400px]">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h2 className="text-lg font-bold text-red-600 mb-2">에러 발생</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => navigate('/agent-logs')}
              className="mt-4 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              목록으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  const competencies = data?.stage1_evidence ? Object.keys(data.stage1_evidence) : [];

  return (
    <div className="min-h-screen">
      <div className="container mx-auto px-8 py-8 max-w-[1800px]">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6 pb-6 border-b border-gray-200">
          <div>
            <button
              onClick={() => navigate('/agent-logs')}
              className="text-gray-500 hover:text-blue text-sm mb-2 flex items-center gap-1"
            >
              <span>←</span> 목록으로
            </button>
            <h1 className="text-2xl font-bold text-blue">
              Evaluation #{data?.evaluation_id} - Agent Logs
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              Interview #{data?.interview_id} | 실행 시간: {data?.evaluation_run_ts}
            </p>
          </div>
          <div className="text-right bg-blue-50 px-6 py-4 rounded-lg">
            <div className="text-3xl font-bold text-blue">
              {data?.execution_summary?.final_score?.toFixed(1)}점
            </div>
            <div className="text-sm text-gray-600">
              신뢰도 {(data?.execution_summary?.confidence_score * 100)?.toFixed(0)}%
            </div>
          </div>
        </div>

        <div className="flex gap-6">
          {/* 왼쪽: Stage 네비게이션 */}
          <div className="w-64 shrink-0">
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-4">Pipeline Stages</h3>
              <div className="space-y-2">
                {STAGES.map((stage) => (
                  <button
                    key={stage.id}
                    onClick={() => setSelectedStage(stage.id)}
                    className={`w-full text-left p-3 rounded-lg transition-all ${
                      selectedStage === stage.id
                        ? 'bg-blue text-white'
                        : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <div className="font-medium text-sm">{stage.name}</div>
                    <div className={`text-xs ${selectedStage === stage.id ? 'text-blue-100' : 'text-gray-500'}`}>
                      {stage.title}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* 에이전트 아키텍처 다이어그램 */}
            <div className="bg-white border border-gray-200 rounded-lg p-4 mt-4">
              <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Agent Architecture</h3>
              <AgentArchitectureDiagram logs={data?.execution_logs || []} />
            </div>
          </div>

          {/* 중앙: Stage 상세 */}
          <div className="flex-1 min-w-0">
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              {selectedStage === 1 && (
                <Stage1View
                  data={data?.stage1_evidence}
                  competencies={competencies}
                  selectedCompetency={selectedCompetency}
                  setSelectedCompetency={setSelectedCompetency}
                />
              )}
              {selectedStage === 2 && <Stage2View data={data?.stage2_aggregator} />}
              {selectedStage === 3 && <Stage3View data={data?.stage3_final} />}
              {selectedStage === 4 && <Stage4View data={data?.stage4_presentation} />}
            </div>
          </div>

          {/* 오른쪽: 역량 상세 (Stage 1일 때만) */}
          {selectedStage === 1 && selectedCompetency && data?.stage1_evidence?.[selectedCompetency] && (
            <div className="w-80 shrink-0">
              <div className="bg-white border border-gray-200 rounded-lg p-4 sticky top-4">
                <CompetencyDetail
                  name={selectedCompetency}
                  data={data.stage1_evidence[selectedCompetency]}
                  segments={data?.stage2_aggregator?.segment_evaluations_with_resume?.filter(
                    (s) => s.competency === selectedCompetency
                  )}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// 역량 순서 정의 (공통 → 직무)
const COMPETENCY_ORDER = [
  // 공통역량 (5개)
  'problem_solving',
  'organizational_fit',
  'growth_potential',
  'interpersonal_skill',
  'achievement_motivation',
  // 직무역량 (5개)
  'customer_journey_marketing',
  'md_data_analysis',
  'seasonal_strategy_kpi',
  'stakeholder_collaboration',
  'value_chain_optimization',
];

// Stage 1: 역량별 병렬 평가
// Stage 1: 역량별 병렬 평가
const Stage1View = ({ data, competencies, selectedCompetency, setSelectedCompetency }) => {
  if (!data) return <div className="text-gray-400 text-center py-10">데이터 없음</div>;

  // 공통역량 / 직무역량 분리
  const commonCompetencies = COMPETENCY_ORDER.slice(0, 5).filter(c => competencies.includes(c));
  const jobCompetencies = COMPETENCY_ORDER.slice(5).filter(c => competencies.includes(c));

  const CompetencyCard = ({ comp }) => {
    const compData = data[comp];
    const score = compData?.overall_score || 0;
    const isSelected = selectedCompetency === comp;
    
    // 1. Local state for the modal
    const [isModalOpen, setIsModalOpen] = useState(false);

    // 2. Prepare data object for the Modal
    // The modal expects specific keys (competencyDisplayName, etc.) which might need to be injected
    const modalData = {
      ...compData, // Spread the raw data (confidence, perspectives, etc.)
      competencyKey: comp,
      competencyDisplayName: COMPETENCY_NAMES[comp] || comp,
      overallScore: score,
      // Ensure confidence structure exists if API differs slightly
      confidence: compData.confidence || compData.confidence_v2 || { overallConfidence: 0 } 
    };

    const handleClick = () => {
      setSelectedCompetency(comp); // Update the right-side panel
      setIsModalOpen(true);        // Open the modal
    };

    const handleCloseModal = (e) => {
      e?.stopPropagation(); // Prevent event bubbling
      setIsModalOpen(false);
    }

    return (
      <>
        {/* 3. Render the Modal */}
        <CompetencyDetailModal
          isOpen={isModalOpen}
          onClose={handleCloseModal}
          competency={modalData}
        />

        {/* 4. Card UI with Click Handler */}
        <div
          onClick={handleClick}
          className={`p-4 rounded-lg cursor-pointer transition-all border ${
            isSelected
              ? 'border-blue bg-blue-50 shadow-sm'
              : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
          }`}
        >
          <div className="flex justify-between items-start mb-3">
            <div>
              <div className="font-semibold text-gray-900">
                {COMPETENCY_NAMES[comp] || comp}
              </div>
              <div className="text-xs text-gray-400">{comp}</div>
            </div>
            <div className={`text-2xl font-bold ${
              score >= 70 ? 'text-green-600' :
              score >= 50 ? 'text-yellow-600' : 'text-red-500'
            }`}>
              {score}
            </div>
          </div>
          <div className="space-y-1">
            {compData?.strengths?.slice(0, 1).map((s, i) => (
              <div key={i} className="text-xs text-green-600 truncate flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-green-500 shrink-0" />
                {s}
              </div>
            ))}
            {compData?.weaknesses?.slice(0, 1).map((w, i) => (
              <div key={i} className="text-xs text-red-500 truncate flex items-center gap-1">
                <span className="w-1 h-1 rounded-full bg-red-500 shrink-0" />
                {w}
              </div>
            ))}
          </div>
        </div>
      </>
    );
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Stage 1: 역량별 병렬 평가</h2>
        <p className="text-gray-500 text-sm mt-1">10개의 CompetencyAgent가 병렬로 각 역량을 평가합니다.</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* 왼쪽: 공통역량 */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 mb-3">공통역량</h3>
          <div className="space-y-3">
            {commonCompetencies.map((comp) => (
              <CompetencyCard key={comp} comp={comp} />
            ))}
          </div>
        </div>

        {/* 오른쪽: 직무역량 */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 mb-3">직무역량</h3>
          <div className="space-y-3">
            {jobCompetencies.map((comp) => (
              <CompetencyCard key={comp} comp={comp} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Stage 2: 통합 및 검증
const Stage2View = ({ data }) => {
  if (!data) return <div className="text-gray-400 text-center py-10">데이터 없음</div>;

  const segments = data.segment_evaluations_with_resume || [];
  const verifiedCount = segments.filter((s) => s.resume_verification?.verified).length;
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
    <ResumeVerificationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        resumeUrl="/resume.pdf"
    />
    <div>
      <div className='flex items-start justify-between'>
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900">Stage 2: 증거 신뢰도 검증</h2>
          <p className="text-gray-500 text-sm mt-1">Resume 검증, 신뢰도 계산, 세그먼트 중복 확인을 수행합니다.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} variant='primary' >
            검증 결과 보기
        </Button>
      </div>
      {/* 통계 카드 */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-blue">{segments.length}</div>
          <div className="text-xs text-gray-500">총 세그먼트</div>
        </div>
        <div className="bg-green-50 border border-green-200 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-green-600">{verifiedCount}</div>
          <div className="text-xs text-gray-500">Resume 검증됨</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-yellow-600">{data.low_confidence_list?.length || 0}</div>
          <div className="text-xs text-gray-500">Low Confidence</div>
        </div>
        <div className="bg-purple-50 border border-purple-200 p-4 rounded-lg text-center">
          <div className="text-2xl font-bold text-purple-600">{data.segment_overlap_adjustments?.length || 0}</div>
          <div className="text-xs text-gray-500">중복 조정</div>
        </div>
      </div>

      {/* 세그먼트 목록 */}
      <h3 className="font-semibold text-gray-900 mb-3">세그먼트별 평가</h3>
      <div className="space-y-3 max-h-[650px] overflow-y-auto">
        {segments.slice(0, 30).map((seg, idx) => (
          <div key={idx} className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
            <div className="flex justify-between items-start mb-2">
              <Badge classname="text-xs bg-blue-100 text-blue px-2">
                {COMPETENCY_NAMES[seg.competency] || seg.competency}
              </Badge>
              <span className={`text-lg font-bold ${
                seg.score >= 70 ? 'text-green-600' :
                seg.score >= 50 ? 'text-yellow-600' : 'text-red-500'
              }`}>
                {seg.score}점
              </span>
            </div>
            <p className="text-sm text-gray-700 mb-2 line-clamp-2">"{seg.quote_text}"</p>
            {seg.resume_verification?.verified && (
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-1 rounded ${
                  seg.resume_verification.strength === 'high'
                    ? 'bg-green-100 text-green-700'
                    : seg.resume_verification.strength === 'medium'
                    ? 'bg-yellow-100 text-yellow-700'
                    : 'bg-gray-100 text-gray-600'
                }`}>
                  Resume: {seg.resume_verification.strength}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
    </>
  );
};

// Stage 3: 최종 결과
const Stage3View = ({ data }) => {
  if (!data) return <div className="text-gray-400 text-center py-10">데이터 없음</div>;

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Stage 3: 최종 결과 생성</h2>
        <p className="text-gray-500 text-sm mt-1">모든 평가를 통합하여 최종 점수와 분석을 생성합니다.</p>
      </div>

      {/* 최종 점수 */}
      <div className="bg-gray-50 border border-gray-200 p-6 rounded-lg mb-6">
        <div className="grid grid-cols-3 gap-6 text-center">
          <div>
            <div className="text-4xl font-bold text-blue">{data.final_score?.toFixed(1)}</div>
            <div className="text-sm text-gray-500 mt-1">최종 점수</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-green-600">{(data.avg_confidence * 100)?.toFixed(0)}%</div>
            <div className="text-sm text-gray-500 mt-1">평균 신뢰도</div>
          </div>
          <div>
            <div className="text-4xl font-bold text-purple-600">{data.final_reliability || 'N/A'}</div>
            <div className="text-sm text-gray-500 mt-1">신뢰성 등급</div>
          </div>
        </div>
      </div>

      {/* 신뢰도 노트 */}
      {data.reliability_note && (
        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-6">
          <h3 className="font-semibold text-gray-900 mb-2">신뢰도 분석</h3>
          <p className="text-sm text-gray-700">{data.reliability_note}</p>
        </div>
      )}

      {/* Final Result JSON */}
      {data.final_result && (
        <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">Final Result (JSON)</h3>
          <pre className="text-xs text-gray-600 overflow-auto max-h-120 bg-white p-3 rounded border border-gray-200">
            {JSON.stringify(data.final_result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

// Stage 4: 프레젠테이션
const Stage4View = ({ data }) => {
  if (!data) return <div className="text-gray-400 text-center py-10">데이터 없음</div>;

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Stage 4: 프레젠테이션 포맷</h2>
        <p className="text-gray-500 text-sm mt-1">프론트엔드에 표시할 최종 포맷입니다.</p>
      </div>

      <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
        <pre className="text-xs text-gray-600 overflow-auto max-h-[600px] bg-white p-3 rounded border border-gray-200">
          {JSON.stringify(data, null, 2)}
        </pre>
      </div>
    </div>
  );
};

// 에이전트 아키텍처 다이어그램
const AgentArchitectureDiagram = ({ logs }) => {
  // 로그에서 stage별 데이터 추출
  const batchEval = logs.find(l => l.node === 'batch_evaluation');
  const aggregator = logs.find(l => l.node === 'aggregator');
  const finalIntegration = logs.find(l => l.node === 'final_integration');
  const presentation = logs.find(l => l.node === 'presentation_formatter');

  const NodeBox = ({ label, time, status = 'completed', small = false }) => (
    <div className={`
      ${small ? 'px-2 py-1' : 'px-3 py-2'}
      bg-white border-2 rounded-lg text-center
      ${status === 'completed' ? 'border-green-400' : 'border-gray-300'}
    `}>
      <div className={`font-medium ${small ? 'text-[10px]' : 'text-xs'} text-gray-700`}>{label}</div>
      {time && <div className={`${small ? 'text-[9px]' : 'text-[10px]'} text-gray-400`}>{time}s</div>}
    </div>
  );

  const Arrow = ({ vertical = false }) => (
    <div className={`flex ${vertical ? 'flex-col items-center py-1' : 'items-center px-1'}`}>
      <div className={`${vertical ? 'w-0.5 h-3' : 'h-0.5 w-3'} bg-gray-300`} />
      <div className={`
        w-0 h-0
        ${vertical
          ? 'border-l-[4px] border-l-transparent border-r-[4px] border-r-transparent border-t-[5px] border-t-gray-300'
          : 'border-t-[4px] border-t-transparent border-b-[4px] border-b-transparent border-l-[5px] border-l-gray-300'
        }
      `} />
    </div>
  );

  return (
    <div className="py-2">
      {/* Stage 1: Parallel Agents */}
      <div className="mb-2">
        <div className="text-[10px] text-gray-400 mb-1 text-center">Stage 1</div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
          <div className="text-[10px] text-blue font-medium text-center mb-2">Parallel Evaluation</div>
          <div className="grid grid-cols-5 gap-1">
            {['PS', 'OF', 'GP', 'IS', 'AM', 'CJ', 'DA', 'SK', 'SC', 'VC'].map((agent, i) => (
              <div key={i} className="bg-white border border-green-300 rounded px-1 py-0.5 text-center">
                <div className="text-[9px] font-medium text-gray-600">{agent}</div>
              </div>
            ))}
          </div>
          {batchEval && (
            <div className="text-[10px] text-gray-500 text-center mt-2">
              {batchEval.duration_seconds?.toFixed(1)}s | {batchEval.competencies_evaluated || 10} agents
            </div>
          )}
        </div>
      </div>

      <Arrow vertical />

      {/* Stage 2: Aggregator */}
      <div className="mb-2">
        <div className="text-[10px] text-gray-400 mb-1 text-center">Stage 2</div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-2">
          <div className="flex justify-center gap-2">
            <NodeBox label="Resume Verify" small />
            <NodeBox label="Confidence" small />
            <NodeBox label="Overlap" small />
          </div>
          {aggregator && (
            <div className="text-[10px] text-gray-500 text-center mt-2">
              {aggregator.duration_seconds?.toFixed(1)}s | {aggregator.segments_processed || 0} segments
            </div>
          )}
        </div>
      </div>

      <Arrow vertical />

      {/* Stage 3: Final Integration */}
      <div className="mb-2">
        <div className="text-[10px] text-gray-400 mb-1 text-center">Stage 3</div>
        <NodeBox
          label="Final Integration"
          time={finalIntegration?.duration_seconds?.toFixed(1)}
        />
      </div>

      <Arrow vertical />

      {/* Stage 4: Presentation */}
      <div>
        <div className="text-[10px] text-gray-400 mb-1 text-center">Stage 4</div>
        <NodeBox
          label="Presentation"
          time={presentation?.duration_seconds?.toFixed(1)}
        />
      </div>

      {/* Total Time */}
      <div className="mt-3 pt-2 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          Total: {logs.reduce((sum, l) => {
            // 중복 로그 방지 (같은 node는 한번만)
            return sum;
          }, 0) || ((batchEval?.duration_seconds || 0) + (aggregator?.duration_seconds || 0) + (finalIntegration?.duration_seconds || 0) + (presentation?.duration_seconds || 0)).toFixed(1)}s
        </div>
      </div>
    </div>
  );
};

// 역량 상세 패널
const CompetencyDetail = ({ name, data, segments }) => {
  return (
    <div>
      <h3 className="text-lg font-bold text-gray-900">{COMPETENCY_NAMES[name] || name}</h3>
      <p className="text-xs text-gray-400 mb-4">{name}</p>

      {/* 점수 */}
      <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg mb-4 text-center">
        <div className="text-3xl font-bold text-blue">{data.overall_score}점</div>
        {data.confidence_v2 && (
          <div className="text-sm text-gray-500 mt-1">
            신뢰도: {(data.confidence_v2 * 100).toFixed(0)}%
          </div>
        )}
      </div>

      {/* 강점 */}
      {data.strengths?.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-green-600 mb-2">강점</h4>
          <ul className="space-y-1">
            {data.strengths.slice(0, 3).map((s, i) => (
              <li key={i} className="text-sm text-gray-700 pl-3 border-l-2 border-green-400">
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 약점 */}
      {data.weaknesses?.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-red-500 mb-2">약점</h4>
          <ul className="space-y-1">
            {data.weaknesses.slice(0, 3).map((w, i) => (
              <li key={i} className="text-sm text-gray-700 pl-3 border-l-2 border-red-400">
                {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Key Observations */}
      {data.key_observations?.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-semibold text-blue mb-2">핵심 관찰</h4>
          <ul className="space-y-1">
            {data.key_observations.slice(0, 3).map((obs, i) => (
              <li key={i} className="text-sm text-gray-700 pl-3 border-l-2 border-blue">
                {obs}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* 세그먼트 */}
      {segments?.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-600 mb-2">관련 세그먼트 ({segments.length}개)</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {segments.slice(0, 5).map((seg, idx) => (
              <div key={idx} className="bg-gray-50 border border-gray-200 p-3 rounded text-sm">
                <p className="text-gray-700 line-clamp-2 mb-1">"{seg.quote_text}"</p>
                <div className="flex gap-2 text-xs">
                  <span className="text-yellow-600">점수: {seg.score}</span>
                  {seg.resume_verification?.verified && (
                    <span className="text-green-600">Resume: {seg.resume_verification.strength}</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentLogs;
