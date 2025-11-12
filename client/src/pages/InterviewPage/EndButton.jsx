import Button from '@components/Button';
import ConfirmModal from '@components/ConfirmModal';
import {useState} from 'react';
import {useNavigate} from 'react-router-dom';

const EndButton = () => {
  const navigate = useNavigate();
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  return (
    <div className='flex justify-end'>
      <Button
        className='px-5'
        variant='secondary'
        onClick={() => setShowConfirmModal(true)}>
        인터뷰 마치기
      </Button>

      <ConfirmModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={() => navigate('/candidate/done')}
        title='인터뷰 완료하기'
        message='인터뷰를 종료하고 결과 페이지로 이동합니다.'
        confirmText='종료하기'
        cancelText='취소'
        variant='primary'
      />
    </div>
  );
};

export default EndButton;
