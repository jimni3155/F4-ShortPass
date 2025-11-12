import Button from '@components/Button';
import exit from '@assets/svg/exit.svg';
import ConfirmModal from '@components/ConfirmModal';
import {useState} from 'react';
import {useNavigate} from 'react-router-dom';

const InterviewPageLayout = ({children}) => {
  const navigate = useNavigate();
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  return (
    <div className='flex min-h-screen bg-linear-to-br from-dark to-black'>
      <aside className='flex w-20 flex-col items-center justify-end bg-dark border-r border-gray-800 py-6'>
        <Button
          variant='ghost'
          onClick={() => {
            setShowConfirmModal(true);
          }}
          className='text-white hover:bg-gray-800 hover:text-white p-2.5 hover:rounded-lg'>
          <img src={exit} alt='나가기' className='scale-x-[-1] h-5 w-5' />
        </Button>
      </aside>
      <main className='w-full flex flex-col p-10 py-10 gap-10'>{children}</main>

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
    </div>
  );
};

export default InterviewPageLayout;
