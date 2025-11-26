import Button from '@components/Button';
import {useEffect, useRef, useState} from 'react';

const InterviewLog = ({messages = [], currentStt = ''}) => {
  const messagesEndRef = useRef(null);

  // 메세지가 추가될 때마다 스크롤 하단으로 이동
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({behavior: 'smooth'});
  }, [messages, currentStt]);

  return (
    <div className='w-90 relative flex flex-col border-l border-gray-800 bg-dark'>
      <div className='border-b border-gray-800 p-4 flex items-center justify-between'>
        <h2 className='text-lg font-semibold text-white'>면접 기록</h2>
      </div>

      {/* 로그 내용 영역 */}
      <div className='flex-1 overflow-y-auto p-4 space-y-3'>
        {/* 1. 확정된 메시지들 (질문 & 답변) */}
        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`rounded-lg p-4 ${
              message.type === 'question'
                ? 'border border-primary bg-primary/10'
                : 'border border-green-500 bg-green-500/10'
            }`}>
            <div className='mb-1 text-xs font-medium text-gray-400'>
              {message.type === 'question' ? '면접관 질문' : '지원자 답변'}
            </div>
            <p className='text-sm leading-relaxed text-white'>{message.text}</p>
          </div>
        ))}

        {/* 2. 실시간 인식 중인 텍스트 (답변 중일 때만 표시) */}
        {currentStt && (
          <div className='rounded-lg border border-green-500/50 bg-green-500/5 p-4 opacity-80'>
            <div className='mb-1 text-xs font-medium text-gray-400 flex items-center gap-2'>
              <span>답변 중...</span>
              <div className='flex gap-1'>
                <div className='h-1 w-1 animate-pulse rounded-full bg-green-500' />
                <div className='h-1 w-1 animate-pulse rounded-full bg-green-500 delay-75' />
                <div className='h-1 w-1 animate-pulse rounded-full bg-green-500 delay-150' />
              </div>
            </div>
            <p className='text-sm leading-relaxed text-white'>{currentStt}</p>
          </div>
        )}

        {/* 스크롤 앵커 */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default InterviewLog;
