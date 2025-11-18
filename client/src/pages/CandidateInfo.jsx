import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import InputField from '../components/InputField';
import Select from '../components/Select';
import PdfUpload from '../components/FileUpload';
import Button from '../components/Button';
import loader from '../assets/svg/loader.svg';
import {saveCandidate} from '../apis/applicant.js';

const steps = [
  {id: 1, title: '기본 인적 사항', description: 'Basic Information'},
  {id: 2, title: '희망 직무', description: 'Desired Role'},
  {id: 3, title: '문서 업로드', description: 'Document Upload'},
];

const genderOptions = [
  {id: 0, name: '남성'},
  {id: 1, name: '여성'},
  {id: 2, name: '기타'},
];

const CandidateInfo = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);

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
    /\S+@\S+\.\S+/.test(formData.email);

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
      alert(
        `지원자 정보 저장 실패: ${
          error.message || '알 수 없는 오류가 발생했습니다.'
        }`
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className='max-w-7xl px-15 py-12 min-h-screen'>
      <div className='flex'>
        <nav className='w-64 shrink-0 my-auto hidden md:block'>
          <div className='sticky top-8'>
            <h2 className='text-sm font-semibold text-gray-500 uppercase mb-6'>
              Application Steps
            </h2>
            <div className='space-y-4'>
              {steps.map((step) => (
                <div
                  key={step.id}
                  className={`flex items-start gap-4 ${
                    currentStep === step.id
                      ? 'text-blue-600'
                      : currentStep > step.id
                      ? 'text-green-600'
                      : 'text-gray-400'
                  }`}>
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                      currentStep === step.id
                        ? 'bg-blue-100 text-blue-600 font-semibold'
                        : currentStep > step.id
                        ? 'bg-green-100 text-green-600'
                        : 'bg-gray-100 text-gray-400'
                    }`}>
                    {currentStep > step.id ? (
                      <Check className='w-4 h-4' />
                    ) : (
                      step.id
                    )}
                  </div>
                  <div className='pt-0.5'>
                    <div className='font-medium text-sm'>{step.title}</div>
                    <div className='text-xs text-gray-500 mt-0.5'>
                      {step.description}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </nav>

        <div className='flex-1 max-w-3xl mx-auto'>
          <div className='flex flex-col flex-1'>
            {/* Form header */}
            <div className='space-y-2 text-center py-10'>
              <h1 className='text-3xl font-bold'>기본 인적 사항</h1>
              <p className='text-grey'>
                면접을 시작하기 위해 필요한 정보를 입력해주세요
              </p>
            </div>

            <form
              onSubmit={handleSubmit}
              className='w-full flex flex-col gap-6'>
              {currentStep === 1 && (
                <div className='w-full grid grid-cols gap-6'>
                  <InputField
                    label='이름'
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({...formData, name: e.target.value})
                    }
                    placeholder='홍길동'
                    required
                  />

                  <InputField
                    label='전화번호'
                    type='tel'
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({...formData, email: e.target.value})
                    }
                    placeholder='010-0000-0000'
                    required
                  />

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

                  <div className='w-full grid grid-cols-1 gap-6 md:grid-cols-2'>
                    <div className='md:col-span-1'>
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
                    <div className='md:col-span-1'>
                      <InputField
                        label='생년월일'
                        type='date'
                        value={formData.birthdate}
                        onChange={(e) =>
                          setFormData({
                            ...formData,
                            birthdate: e.target.value,
                          })
                        }
                      />
                    </div>
                  </div>

                  <Select
                    label='최종학력'
                    options={genderOptions}
                    value={formData.gender}
                    onChange={(e) =>
                      setFormData({...formData, gender: e.target.value})
                    }
                    placeholder='최종학력 선택'
                  />

                  <InputField
                    label='학교명'
                    type='text'
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({...formData, email: e.target.value})
                    }
                    placeholder='학교명을 입력하세요.'
                  />

                  <InputField
                    label='전공'
                    type='text'
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({...formData, email: e.target.value})
                    }
                    placeholder='전공학과를 입력하세요.'
                  />
                </div>
              )}

              {currentStep === 2 && (
                <div className='w-full grid grid-cols gap-6'> </div>
              )}

              {/* <PdfUpload
                label='포트폴리오 PDF'
                file={formData.portfolioPdf}
                onFileChange={(file) =>
                  setFormData({...formData, portfolioPdf: file})
                }
                onRemove={() => setFormData({...formData, portfolioPdf: null})}
              /> */}

              <div className='flex gap-5 justify-between items-center mt-4'>
                <Button
                  type='button'
                  variant='ghost'
                  className={isLoading ? 'hidden' : ''}
                  onClick={() => navigate('/')}
                  disabled={isLoading}>
                  이전
                </Button>
                {currentStep === 3 ? (
                  <Button
                    type='submit'
                    className={
                      isLoading ? 'w-fit p-3 px-4 whitespace-nowrap' : ''
                    }
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
                      '제출하기'
                    )}
                  </Button>
                ) : (
                  <Button
                    type='button'
                    onClick={() => setCurrentStep(currentStep++)}>
                    다음
                  </Button>
                )}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateInfo;
