import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import InputField from '../components/InputField';
import Select from '../components/Select';
import PdfUpload from '../components/FileUpload';
import Button from '../components/Button';
import loader from '../assets/svg/loader.svg';
import {saveCandidate} from '../apis/applicant.js';

const CandidateInfo = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    gender: '',
    education: '',
    birthdate: '',
    portfolioPdf: null,
  });

  const [isLoading, setIsLoading] = useState(false);

  const isFormValid =
    formData.name.trim() &&
    formData.email.trim() &&
    /\S+@\S+\.\S+/.test(formData.email) 

  const genderOptions = [
    {id: 0, name: '남성'},
    {id: 1, name: '여성'},
    {id: 2, name: '기타'},
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading || !isFormValid) return;

    setIsLoading(true);

    try {
      console.log('Submitting candidate data...');

      // saveCandidate API 호출
      const savedCandidate = await saveCandidate(
        {
          name: formData.name,
          email: formData.email,
          gender: formData.gender || undefined,
          education: formData.education || undefined,
          birthdate: formData.birthdate || undefined,
        },
        formData.portfolioPdf
      );

      console.log('Candidate saved successfully:', savedCandidate);

      // 서버에서 받은 candidate ID를 로컬 스토리지에 저장
      localStorage.setItem('currentCandidateId', savedCandidate.id);

      // (선택적) 800ms 대기 후 다음 페이지로 이동
      await new Promise((resolve) => setTimeout(resolve, 800));

      console.log('Navigating to /candidate/start...');
      navigate('/candidate/start');
    } catch (error) {
      console.error('Failed to save candidate:', error);
      alert(`지원자 정보 저장 실패: ${error.message || '알 수 없는 오류가 발생했습니다.'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='w-full min-h-screen flex justify-center my-10'>
      <div className='w-2/3 flex flex-col mx-auto'>
        {/* Form header */}
        <div className='space-y-2 text-center py-10'>
          <h1 className='text-3xl font-bold'>지원자 정보</h1>
          <p className='text-grey'>
            면접을 시작하기 위해 필요한 정보를 입력해주세요
          </p>
        </div>

        <form onSubmit={handleSubmit} className='w-full flex flex-col gap-6'>
          <div className='w-full grid grid-cols-1 gap-6 md:grid-cols-10'>
            <div className='md:col-span-4'>
              <InputField
                label='이름'
                value={formData.name}
                onChange={(e) =>
                  setFormData({...formData, name: e.target.value})
                }
                placeholder='홍길동'
                required
              />
            </div>
            <div className='md:col-span-6'>
              <InputField
                label='이메일'
                type='email'
                value={formData.email}
                onChange={(e) =>
                  setFormData({...formData, email: e.target.value})
                }
                placeholder='example@email.com'
                required
              />
            </div>
          </div>

          <div className='w-full grid grid-cols-1 gap-6 md:grid-cols-10'>
            <div className='md:col-span-4'>
              <InputField
                label='학력'
                value={formData.education}
                onChange={(e) =>
                  setFormData({...formData, education: e.target.value})
                }
                placeholder='예: 서울대학교 컴퓨터공학과'
              />
            </div>
            <div className='md:col-span-3'>
              <Select
                label='성별'
                options={genderOptions}
                value={formData.gender}
                onChange={(e) =>
                  setFormData({...formData, gender: e.target.value})
                }
                placeholder='남성, 여성, 기타'
              />
            </div>
            <div className='md:col-span-3'>
              <InputField
                label='생년월일'
                type='date'
                value={formData.birthdate}
                onChange={(e) =>
                  setFormData({...formData, birthdate: e.target.value})
                }
                placeholder='선택하세요'
              />
            </div>
          </div>

          <PdfUpload
            label='포트폴리오 PDF'
            file={formData.portfolioPdf}
            onFileChange={(file) =>
              setFormData({...formData, portfolioPdf: file})
            }
            onRemove={() => setFormData({...formData, portfolioPdf: null})}
          />

          <div className='flex gap-5 justify-center items-center mt-4'>
            <Button
              type='button'
              variant='primary'
              className={isLoading ? 'hidden' : ''}
              onClick={() => navigate('/')}
              disabled={isLoading}>
              뒤로
            </Button>
            <Button
              type='submit'
              className={isLoading ? 'w-fit p-3 px-4 whitespace-nowrap' : ''}
              disabled={!isFormValid || isLoading}>
              {isLoading ? (
                <span className='flex items-center gap-2'>
                  <img
                    className='w-4 h-4 animate-spin'
                    src={loader}
                    alt='로딩'
                  />
                  질문 세트를 준비하고 있습니다…
                </span>
              ) : (
                '다음'
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CandidateInfo;