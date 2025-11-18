import Button from '@components/Button';
import {useRef, useState} from 'react';

const InterviewLog = () => {
  const QUESTIONS = [
    {id: 1, text: '자기소개를 해주세요.', audioUrl: null},
    {id: 2, text: '이 직무에 지원한 이유는 무엇인가요?', audioUrl: null},
    {id: 3, text: '본인의 강점과 약점을 말씀해주세요.', audioUrl: null},
    {
      id: 4,
      text: '팀 프로젝트에서 어려움을 겪은 경험이 있나요?',
      audioUrl: null,
    },
    {id: 5, text: '5년 후 본인의 모습은 어떨 것 같나요?', audioUrl: null},
    {id: 6, text: '마지막으로 하고 싶은 말씀이 있나요?', audioUrl: null},
  ];
  async function mockSTT() {
    const words = [
      'Sure.',
      'My name is',
      'John Doe,',
      'and I',
      'recently graduated',
      'with a degree',
      'in marketing.',
      "I've always been",
      'passionate about',
      'creating and',
      'sharing stories,',
    ];

    for (const word of words) {
      await new Promise((resolve) => setTimeout(resolve, 300));
      callback(word);
    }
  }

  const [isLogOpen, setIsLogOpen] = useState(true);
  const [currentAnswerText, setCurrentAnswerText] = useState('');
  const [messages, setMessages] = useState([
    {type: 'question', text: QUESTIONS[0].text, timestamp: Date.now()},
  ]);

  const messagesEndRef = null;
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);

  const [logWidth, setLogWidth] = useState(384); // 96 * 4 = 384px (w-96)
  const [isResizing, setIsResizing] = useState(false);
  const resizeStartXRef = useRef(0);
  const resizeStartWidthRef = useRef(0);

  const currentQuestion = QUESTIONS[currentQuestionIndex];

  return (
    <>
      {isLogOpen && (
        <div
          className='relative flex flex-col border-l border-gray-800 bg-gray-900'
          style={{width: `${logWidth}px`}}>
          {/* Resize Handle */}
          <div
            className='absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-[#8B5CF6] transition-colors'
            // onMouseDown={handleResizeStart}
          />
          <div className='border-b border-gray-800 p-4 flex items-center justify-between'>
            <h2 className='text-lg font-semibold text-white'>대화 기록</h2>
            <Button
              variant='ghost'
              size='icon'
              onClick={() => setIsLogOpen(false)}
              className='text-gray-400 hover:bg-gray-800 hover:text-white'>
              {/* <ChevronRight className='h-5 w-5' /> */}
            </Button>
          </div>
          <div className='flex-1 overflow-y-auto p-4 space-y-3'>
            {messages.map((message, idx) => (
              <div
                key={idx}
                className={`rounded-lg p-4 ${
                  message.type === 'question'
                    ? 'border border-[#8B5CF6] bg-[#8B5CF6]/10'
                    : 'border border-green-500 bg-green-500/10'
                }`}>
                <div className='mb-1 text-xs font-medium text-gray-400'>
                  {message.type === 'question' ? 'AI 면접관' : '지원자 답변'}
                </div>
                <p className='text-sm leading-relaxed text-white'>
                  {message.text}
                </p>
              </div>
            ))}
            {/* Show current answer being transcribed in real-time */}
            {false && currentAnswerText && (
              <div className='rounded-lg border border-green-500 bg-green-500/10 p-4'>
                <div className='mb-1 text-xs font-medium text-gray-400'>
                  지원자 답변
                </div>
                <p className='text-sm leading-relaxed text-white'>
                  {currentAnswerText}
                </p>
                <div className='mt-2 flex items-center gap-1'>
                  <div className='h-1 w-1 animate-pulse rounded-full bg-green-500' />
                  <div
                    className='h-1 w-1 animate-pulse rounded-full bg-green-500'
                    style={{animationDelay: '0.2s'}}
                  />
                  <div
                    className='h-1 w-1 animate-pulse rounded-full bg-green-500'
                    style={{animationDelay: '0.4s'}}
                  />
                </div>
              </div>
            )}
            {false && (
              <div className='rounded-lg border border-gray-700 bg-gray-800 p-4 text-center'>
                <div className='mx-auto h-5 w-5 animate-spin rounded-full border-4 border-[#8B5CF6] border-t-transparent' />
                <p className='mt-2 text-xs text-gray-400'>
                  답변을 처리중입니다…
                </p>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {!isLogOpen && (
        <div className='flex flex-col border-l border-gray-800 bg-gray-900'>
          <Button
            variant='ghost'
            size='icon'
            onClick={() => setIsLogOpen(true)}
            className='m-2 text-gray-400 hover:bg-gray-800 hover:text-white'>
            <ChevronLeft className='h-5 w-5' />
          </Button>
        </div>
      )}
    </>
  );
};

export default InterviewLog;
