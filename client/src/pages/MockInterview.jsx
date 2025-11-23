import {useState, useEffect} from 'react';
import {useNavigate, useSearchParams} from 'react-router-dom';
import Button from '../components/Button';
import Badge from '../components/Badge';

// Mock 페르소나 및 질문 데이터
const MOCK_PERSONAS = [
  {
    id: 1,
    companyId: 1,
    companyName: '테크스타트업 A',
    personaName: '김기술 면접관',
    archetype: '분석형',
    description: '기술적 깊이와 문제 해결 능력을 중시하는 시니어 개발자',
    focusAreas: ['Python', 'FastAPI', '시스템 설계', '성능 최적화'],
    avatar: '👨‍💻',
    questions: [
      'Python의 GIL에 대해 설명하고, 멀티쓰레딩 성능 이슈를 어떻게 해결할 수 있나요?',
      'FastAPI에서 비동기 처리를 구현할 때 주의해야 할 점은 무엇인가요?',
      '대용량 트래픽을 처리하기 위한 시스템 아키텍처를 설계한다면 어떻게 하시겠습니까?',
    ],
  },
  {
    id: 2,
    companyId: 2,
    companyName: 'AI 스타트업 B',
    personaName: '박협업 면접관',
    archetype: '지원형',
    description: '팀워크와 커뮤니케이션을 중요시하는 PM 출신 면접관',
    focusAreas: ['협업', '커뮤니케이션', '프로젝트 관리', '문제 해결'],
    avatar: '👩‍💼',
    questions: [
      '팀 프로젝트에서 의견 충돌이 있었을 때 어떻게 해결하셨나요?',
      '비기술 직군과 협업할 때 가장 어려웠던 점은 무엇인가요?',
      '프로젝트 일정이 촉박한 상황에서 우선순위를 어떻게 정하시나요?',
    ],
  },
  {
    id: 3,
    companyId: 3,
    companyName: '핀테크 C',
    personaName: '이성장 면접관',
    archetype: '도전형',
    description: '빠른 성장과 학습 능력을 중시하는 CTO',
    focusAreas: ['학습 능력', '적응력', '성장 마인드', '혁신'],
    avatar: '',
    questions: [
      '최근 1년간 가장 열심히 학습한 기술이나 개념은 무엇인가요?',
      '실패했던 프로젝트에서 어떤 교훈을 얻으셨나요?',
      '우리 회사에서 이루고 싶은 목표는 무엇인가요?',
    ],
  },
];

const MockInterview = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [currentPersonaIndex, setCurrentPersonaIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [conversationHistory, setConversationHistory] = useState([]);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const currentPersona = MOCK_PERSONAS[currentPersonaIndex];
  const currentQuestion = currentPersona.questions[currentQuestionIndex];
  const totalPersonas = MOCK_PERSONAS.length;
  const totalQuestionsPerPersona = currentPersona.questions.length;

  // 전체 진행률 계산
  const totalQuestions = MOCK_PERSONAS.reduce((sum, p) => sum + p.questions.length, 0);
  const currentTotalQuestionNumber =
    MOCK_PERSONAS.slice(0, currentPersonaIndex).reduce((sum, p) => sum + p.questions.length, 0) +
    currentQuestionIndex + 1;
  const progress = (currentTotalQuestionNumber / totalQuestions) * 100;

  // 페르소나 변경 시 인트로 메시지 추가
  useEffect(() => {
    if (currentQuestionIndex === 0) {
      setConversationHistory(prev => [
        ...prev,
        {
          type: 'persona_intro',
          persona: currentPersona,
          timestamp: new Date(),
        },
      ]);
    }
  }, [currentPersonaIndex]);

  const handleSubmitAnswer = () => {
    if (!answer.trim()) {
      alert('답변을 입력해주세요.');
      return;
    }

    // 답변 저장
    setConversationHistory(prev => [
      ...prev,
      {
        type: 'question',
        persona: currentPersona,
        question: currentQuestion,
        timestamp: new Date(),
      },
      {
        type: 'answer',
        answer: answer.trim(),
        timestamp: new Date(),
      },
    ]);

    setAnswer('');
    setIsTransitioning(true);

    // 다음 질문 또는 페르소나로 이동
    setTimeout(() => {
      if (currentQuestionIndex < totalQuestionsPerPersona - 1) {
        // 같은 페르소나의 다음 질문
        setCurrentQuestionIndex(prev => prev + 1);
      } else if (currentPersonaIndex < totalPersonas - 1) {
        // 다음 페르소나로 이동
        setCurrentPersonaIndex(prev => prev + 1);
        setCurrentQuestionIndex(0);
      } else {
        // 모든 면접 완료
        navigate('/candidate/done');
      }
      setIsTransitioning(false);
    }, 1000);
  };

  const isLastQuestion =
    currentPersonaIndex === totalPersonas - 1 &&
    currentQuestionIndex === totalQuestionsPerPersona - 1;

  return (
    <div className='w-full min-h-screen bg-gray-50'>
      {/* 진행률 바 */}
      <div className='w-full h-2 bg-gray-200'>
        <div
          className='h-full bg-primary transition-all duration-500'
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className='container mx-auto px-4 py-8 max-w-4xl'>
        {/* 상단: 현재 페르소나 정보 */}
        <div className='bg-white rounded-xl shadow-md p-6 mb-6'>
          <div className='flex items-start gap-4'>
            <div className='text-6xl'>{currentPersona.avatar}</div>
            <div className='flex-1'>
              <div className='flex items-center gap-3 mb-2'>
                <h2 className='text-2xl font-bold text-gray-900'>
                  {currentPersona.personaName}
                </h2>
                <Badge variant='secondary'>{currentPersona.archetype}</Badge>
              </div>
              <p className='text-sm text-gray-600 mb-3'>
                {currentPersona.companyName} • {currentPersona.description}
              </p>
              <div className='flex flex-wrap gap-2'>
                {currentPersona.focusAreas.map((area, idx) => (
                  <span
                    key={idx}
                    className='px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full'>
                    {area}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 중앙: 질문 영역 */}
        <div className='bg-white rounded-xl shadow-md p-8 mb-6'>
          <div className='mb-4'>
            <span className='text-sm font-medium text-gray-500'>
              질문 {currentQuestionIndex + 1} / {totalQuestionsPerPersona}
              <span className='ml-2 text-xs text-gray-400'>
                (전체 {currentTotalQuestionNumber} / {totalQuestions})
              </span>
            </span>
          </div>

          <div
            className={`transition-opacity duration-300 ${
              isTransitioning ? 'opacity-0' : 'opacity-100'
            }`}>
            <h3 className='text-xl font-semibold text-gray-900 mb-6 leading-relaxed'>
              {currentQuestion}
            </h3>

            <textarea
              placeholder='답변을 입력하세요...'
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              rows={8}
              className='w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary resize-none'
              disabled={isTransitioning}
            />

            <div className='flex justify-between items-center mt-6'>
              <span className='text-sm text-gray-500'>
                {answer.length} 글자
              </span>
              <Button
                onClick={handleSubmitAnswer}
                disabled={isTransitioning || !answer.trim()}
                className='px-6'>
                {isTransitioning
                  ? '처리 중...'
                  : isLastQuestion
                  ? '면접 완료'
                  : '다음 질문'}
              </Button>
            </div>
          </div>
        </div>

        {/* 하단: 페르소나 진행 상황 */}
        <div className='bg-white rounded-xl shadow-md p-6'>
          <h4 className='text-sm font-semibold text-gray-700 mb-4'>면접 진행 상황</h4>
          <div className='flex gap-4'>
            {MOCK_PERSONAS.map((persona, idx) => (
              <div
                key={persona.id}
                className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                  idx === currentPersonaIndex
                    ? 'border-primary bg-primary/5'
                    : idx < currentPersonaIndex
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 bg-gray-50'
                }`}>
                <div className='text-2xl mb-2'>{persona.avatar}</div>
                <div className='text-xs font-medium text-gray-700 mb-1'>
                  {persona.companyName}
                </div>
                <div className='text-xs text-gray-500'>
                  {idx < currentPersonaIndex ? (
                    <span className='text-green-600 font-semibold'>✓ 완료</span>
                  ) : idx === currentPersonaIndex ? (
                    <span className='text-primary font-semibold'>진행 중</span>
                  ) : (
                    <span className='text-gray-400'>대기 중</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 대화 히스토리 (디버깅용, 옵션) */}
        {process.env.NODE_ENV === 'development' && conversationHistory.length > 0 && (
          <div className='mt-6 bg-white rounded-xl shadow-md p-6'>
            <h4 className='text-sm font-semibold text-gray-700 mb-4'>대화 기록</h4>
            <div className='space-y-3 max-h-96 overflow-y-auto'>
              {conversationHistory.map((item, idx) => (
                <div key={idx} className='text-sm'>
                  {item.type === 'persona_intro' ? (
                    <div className='p-3 bg-blue-50 rounded-lg border border-blue-200'>
                      <strong className='text-blue-700'>
                        {item.persona.personaName} 면접 시작
                      </strong>
                    </div>
                  ) : item.type === 'question' ? (
                    <div className='p-3 bg-gray-50 rounded-lg'>
                      <strong className='text-gray-700'>질문:</strong> {item.question}
                    </div>
                  ) : (
                    <div className='p-3 bg-green-50 rounded-lg border border-green-200'>
                      <strong className='text-green-700'>답변:</strong> {item.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MockInterview;
