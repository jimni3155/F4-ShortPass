const AgentPanel = ({
  currentInterviewer,
  currentQuestion,
  currentQuestionIndex,
  turnState,
}) => {
  // 면접관 타입에 따른 색상 테마
  const getTypeColor = (type) => {
    switch (type) {
      case '전략형':
        return 'from-[#4F46E5] to-[#818CF8]'; // 인디고
      case '실행형':
        return 'from-[#059669] to-[#34D399]'; // 에메랄드
      case '조직적합형':
        return 'from-[#D97706] to-[#FBBF24]'; // 앰버
      default:
        return 'from-[#7D63FF] to-[#AB9AFF]'; // 기본 퍼플
    }
  };

  const bgGradient = currentInterviewer
    ? getTypeColor(currentInterviewer.type)
    : 'from-[#7D63FF] to-[#AB9AFF]';

  return (
    <article
      className={`flex flex-col aspect-video rounded-2xl bg-radial-[50%_50%_at_50%_50%] ${bgGradient} p-6 transition-all duration-500`}>
      {/* 면접관 정보 */}
      <div className='flex-1 flex flex-col items-center justify-center'>
        {currentInterviewer ? (
          <>
            <p className='text-xl text-white/80 mb-1'>
              {currentInterviewer.type}
            </p>
            <p className='text-3xl text-white font-bold mb-2'>
              {currentInterviewer.name}
            </p>
            {currentInterviewer.role && (
              <p className='text-sm text-white/70'>{currentInterviewer.role}</p>
            )}
          </>
        ) : (
          <p className='text-3xl text-white font-bold'>AI 인터뷰어</p>
        )}
      </div>

      {/* 질문 표시 영역 */}
      {currentQuestion && (
        <div className={`rounded-xl p-4 backdrop-blur-sm ${
          currentQuestion.isFollowUp
            ? 'bg-yellow-500/20 border border-yellow-500/50'
            : 'bg-black/30'
        }`}>
          <div className='flex items-center gap-2 mb-2'>
            <span className={`text-white text-xs px-2 py-1 rounded-full ${
              currentQuestion.isFollowUp ? 'bg-yellow-500/40' : 'bg-white/20'
            }`}>
              {currentQuestion.isFollowUp ? '꼬리질문' : `Q${currentQuestionIndex}`}
            </span>
            {turnState === 'questioning' && (
              <span className='text-white/70 text-xs animate-pulse'>
                질문 중...
              </span>
            )}
            {turnState === 'answering' && (
              <span className='text-green-300 text-xs'>답변해 주세요</span>
            )}
            {turnState === 'processing' && (
              <span className='text-yellow-300 text-xs animate-pulse'>
                처리 중...
              </span>
            )}
          </div>
          <p className='text-white text-sm leading-relaxed'>
            {currentQuestion.text}
          </p>
        </div>
      )}
    </article>
  );
};

export default AgentPanel;
