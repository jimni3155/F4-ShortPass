import Webcam from 'react-webcam';

const CameraPreview = ({phase = 'answering'}) => {
  return (
    <section className='relative w-2/3 h-120 bg-grey rounded-2xl'>
      <Webcam
        className='w-full h-full object-cover rounded-lg'
        audio={false}
        mirrored={true}
        videoConstraints={{
          width: 1280,
          height: 720,
          facingMode: 'user',
        }}
        muted
        playsInline
      />

      {phase === 'answering' && (
        <div className='absolute left-4 top-4 flex items-center gap-2 rounded-full bg-green px-3 py-1.5'>
          <span className='h-2 w-2 animate-pulse rounded-full bg-white' />
          <span className='text-sm font-medium text-white'>답변 중</span>
        </div>
      )}
    </section>
  );
};

export default CameraPreview;
