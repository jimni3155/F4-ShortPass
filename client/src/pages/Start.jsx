import Button from '../components/Button';
import {useNavigate} from 'react-router-dom';

const Start = () => {
  const navigate = useNavigate();
  return (
    <div className='w-full min-h-screen flex'>
      <div className='flex flex-1 flex-col items-center justify-center gap-15 text-center px-10'>
        <h1 className='text-5xl font-bold'>
          AI가 연결하는 새로운 면접 경험,{' '}
          <span className='text-primary'>FLEX</span>
        </h1>
        {/* Button Group */}
        <div className='flex gap-10'>
          <Button onClick={() => navigate('/candidate/info')}>지원자</Button>
          <Button onClick={() => navigate('/company/info')}>기업</Button>
        </div>
      </div>
    </div>
  );
};

export default Start;

