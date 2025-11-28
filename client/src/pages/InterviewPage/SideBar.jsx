import Button from '@components/Button';
import ConfirmModal from '@components/ConfirmModal';
import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import exit from '@assets/svg/exit.svg';

const SideBar = ({interviewers = [], currentInterviewer}) => {
  const navigate = useNavigate();
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  // 면접관 타입에 따른 색상
  const getTypeColor = (type, isActive) => {
    if (!isActive) return 'bg-gray-700';
    switch (type) {
      case '전략형':
        return 'bg-indigo-600';
      case '실행형':
        return 'bg-emerald-600';
      case '조직적합형':
        return 'bg-amber-600';
      default:
        return 'bg-purple-600';
    }
  };

  return (
    <>
      <aside className='flex w-64 flex-col bg-dark border-r border-gray-800 py-6 px-4'>
        {/* 면접관 목록 */}
        <div className='flex-1'>
          <h3 className='text-gray-400 text-xs font-medium mb-4 uppercase tracking-wider'>
            면접관
          </h3>
          <div className='space-y-2'>
            {interviewers.map((interviewer, idx) => {
              const isActive = currentInterviewer?.id === interviewer.id;
              return (
                <div
                  key={interviewer.id || idx}
                  className={`p-3 rounded-lg transition-all duration-300 ${
                    isActive
                      ? 'bg-gray-700/50 border border-gray-600'
                      : 'bg-transparent'
                  }`}>
                  <div className='flex items-center gap-3'>
                    <div
                      className={`w-2 h-2 rounded-full ${getTypeColor(
                        interviewer.type,
                        isActive
                      )}`}
                    />
                    <div className='flex-1 min-w-0'>
                      <p
                        className={`text-sm font-medium truncate ${
                          isActive ? 'text-white' : 'text-gray-400'
                        }`}>
                        {interviewer.name}
                      </p>
                      <p className='text-xs text-gray-500'>
                        {interviewer.type} · 질문 {interviewer.question_count}개
                      </p>
                    </div>
                    {isActive && (
                      <span className='text-xs text-green-400 animate-pulse'>
                        진행 중
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {interviewers.length === 0 && (
            <p className='text-gray-500 text-sm text-center py-4'>
              면접관 정보 로딩 중...
            </p>
          )}
        </div>

        {/* 나가기 버튼 */}
        <div className='pt-4 border-t border-gray-800'>
          <Button
            variant='ghost'
            onClick={() => setShowConfirmModal(true)}
            className='w-full text-gray-400 hover:text-white hover:bg-gray-800 justify-start gap-2'>
            <img src={exit} alt='나가기' className='scale-x-[-1] h-4 w-4' />
            <span className='text-sm'>나가기</span>
          </Button>
        </div>
      </aside>

      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={() => navigate('/candidate/start')}
        title='인터뷰를 나가시겠습니까?'
        message='현재 진행 중인 인터뷰를 나가시면 지금까지의 답변 내용은 저장되지 않고 모두 삭제됩니다. 정말 나가시겠습니까?'
        confirmText='종료하기'
        cancelText='취소'
        variant='danger'
      />
    </>
  );
};
export default SideBar;
