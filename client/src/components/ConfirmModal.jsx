import x from '@assets/svg/x.svg';

export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'primary',
}) {
  if (!isOpen) return null;

  const buttonColors = {
    primary: 'bg-dark hover:bg-primary text-white',
    danger: 'bg-red hover:bg-red/90 text-white',
  };

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center'>
      <div className='absolute inset-0 bg-black/50' onClick={onClose} />
      <div className='relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6 '>
        <button
          onClick={onClose}
          className='absolute top-4 right-4 p-1 hover:bg-gray-100 rounded transition-colors'>
          <img src={x} className='w-4 h-4' alt='취소' />
        </button>

        <h3 className='text-lg font-semibold text-text mb-2'>{title}</h3>
        <p className='text-gray-600 mb-6'>{message}</p>

        <div className='flex gap-3 justify-end'>
          <button
            onClick={onClose}
            className='cursor-pointer px-4 py-1.5 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium'>
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`cursor-pointer px-4 py-1.5 rounded-lg transition-colors font-medium ${buttonColors[variant]}`}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
