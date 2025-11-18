import {useState} from 'react';

const QUESTIONS = [
  '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
  '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
  '성능 최적화를 위해 수행한 조치를 설명해주세요.',
  '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
  '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
  '성능 최적화를 위해 수행한 조치를 설명해주세요.',
  '성능 최적화를 위해 수행한 조치를 설명해주세요.',
  '최근 프로젝트에서 맡은 역할을 말씀해주세요.',
  '팀 내 협업 중 가장 도전적이었던 순간은 무엇인가요?',
  '성능 최적화를 위해 수행한 조치를 설명해주세요.',
];

const QuestionBar = () => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(1);

  return (
    <article className='mt-6 flex items-center justify-center rounded-lg border border-gray-800 bg-dark/50 px-2 py-4'>
      {QUESTIONS.map((question, index) => (
        <div key={question.id} className='flex items-center'>
          <div
            className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold transition-all ${
              index === currentQuestionIndex
                ? 'bg-white text-dark'
                : index < currentQuestionIndex
                ? 'bg-primary text-white'
                : 'bg-gray-800 text-gray-500'
            }`}>
            {index + 1}
          </div>
          {index < QUESTIONS.length - 1 && (
            <div
              className={`h-0.5 w-12 ${
                index < currentQuestionIndex ? 'bg-primary' : 'bg-gray-800'
              }`}
            />
          )}
        </div>
      ))}
    </article>
  );
};

export default QuestionBar;
