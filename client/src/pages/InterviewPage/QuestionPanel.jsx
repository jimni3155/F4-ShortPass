import help_circle from '@assets/svg/help-circle.svg';
import loader from '@assets/svg/loader.svg';
import {useState} from 'react';

const QuestionPanel = ({
  currentQuestion,
  currentQuestionIndex,
  phase = 'processing',
}) => {
  return (
    <article className='bg-gray-800 border border-gray-700 overflow-y-auto p-4 rounded-2xl'>
      <div className='flex items-center gap-3 text-lg text-white p-3 font-semibold'>
        {phase === 'processing' ? (
          <div className='flex items-center gap-3'>
            {/* <img className='w-4 h-4 animate-spin' src={loader} alt='로딩' /> */}
            <div className='mx-auto h-5 w-5 animate-spin rounded-full border-4 border-white border-t-transparent' />
            답변을 처리중입니다...
          </div>
        ) : (
          <p>
            Q{currentQuestionIndex + 1} : {currentQuestion}
          </p>
        )}
      </div>
    </article>
  );
};

export default QuestionPanel;
