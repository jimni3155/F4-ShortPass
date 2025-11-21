import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import InputField from '../components/InputField';
import Select from '../components/Select';
import PdfUpload from '../components/FileUpload';
import Button from '../components/Button';
import loader from '../assets/svg/loader.svg';
import check from '../assets/svg/check.svg';
import {saveCandidate} from '../apis/applicant.js';
import {roleCategories, subRoles} from '@data/roles';

// -------------------- 상수 정의 --------------------

const STEPS = [
  {id: 1, title: '기본 인적 사항', description: 'Basic Information'},
  {id: 2, title: '희망 직무', description: 'Desired Role'},
  {id: 3, title: '문서 업로드', description: 'Document Upload'},
];

const STEP_TITLES = {
  1: '기본 인적 사항',
  2: '희망 직무',
  3: '문서 업로드',
};

const STEP_DESCRIPTIONS = {
  1: '면접을 시작하기 위해 필요한 정보를 입력해주세요',
  2: '희망하는 직무를 선택해주세요',
  3: '지원에 필요한 서류를 업로드해 주세요 — 이력서, 자기소개서, 포트폴리오',
};

const genderOptions = [
  {id: 0, name: '남성'},
  {id: 1, name: '여성'},
  {id: 2, name: '기타'},
];

const educationOptions = [
  {id: 0, name: '고등학교 졸업'},
  {id: 1, name: '전문학사'},
  {id: 2, name: '학사'},
  {id: 3, name: '석사'},
  {id: 4, name: '박사'},
];

// -------------------- 컴포넌트 --------------------

const CandidateInfo = () => {
  const navigate = useNavigate();

  const [currentStep, setCurrentStep] = useState(1);

  const [formData, setFormData] = useState({
    // 기본 정보
    name: '',
    email: '',
    phone: '',
    gender: '',
    birthdate: '',
    education: '',
    school: '',
    major: '',
    // 파일
    portfolioPdf: null,
    // 직무 선택 (서버로 보낼 거면 나중에 추가)
    roleCategory: '',
    role: '',
    subRole: '',
  });

  const [isLoading, setIsLoading] = useState(false);

  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedRole, setSelectedRole] = useState('');
  const [selectedSubRole, setSelectedSubRole] = useState('');

  // -------------------- 유효성 검사 --------------------

  const isEmailValid = /\S+@\S+\.\S+/.test(formData.email);

  const isBasicInfoValid =
    formData.name.trim() &&
    formData.phone.trim() &&
    formData.email.trim() &&
    isEmailValid;

  const isFinalSubmitValid = isBasicInfoValid && formData.portfolioPdf !== null; // PDF 필수라면

  // -------------------- 핸들러 --------------------

  const handleChange = (key) => (e) => {
    const value = e?.target ? e.target.value : e;
    setFormData((prev) => ({...prev, [key]: value}));
  };

  const handleNextStep = () => {
    setCurrentStep((prev) => Math.min(prev + 1, 3));
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    } else {
      navigate('/');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isLoading || !isFinalSubmitValid) return;

    setIsLoading(true);

    try {
      const payload = {
        name: formData.name,
        email: formData.email,
        gender: formData.gender || undefined,
        education: formData.education || undefined,
        birthdate: formData.birthdate || undefined,
        // 필요하다면 role 정보도 여기에 추가
        // roleCategory: formData.roleCategory || undefined,
        // role: formData.role || undefined,
        // subRole: formData.subRole || undefined,
      };

      const savedCandidate = await saveCandidate(
        payload,
        formData.portfolioPdf
      );

      localStorage.setItem('currentCandidateId', savedCandidate.id);

      await new Promise((resolve) => setTimeout(resolve, 800));

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

  // -------------------- UI 조각 --------------------

  const renderSidebarStep = (step) => {
    let status = 'upcoming';
    if (currentStep === step.id) status = 'current';
    if (currentStep > step.id) status = 'completed';

    const isCurrent = status === 'current';
    const isCompleted = status === 'completed';

    const wrapperClass =
      status === 'current'
        ? 'text-blue-600'
        : status === 'completed'
        ? 'text-green-600'
        : 'text-gray-400';

    const circleClass = [
      'w-8 h-8 rounded-full flex items-center justify-center shrink-0',
      isCurrent && 'bg-blue-100 text-blue-600 font-semibold',
      isCompleted && 'bg-green-100 text-green-600',
      status === 'upcoming' && 'bg-gray-100 text-gray-400',
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div key={step.id} className={`flex items-start gap-4 ${wrapperClass}`}>
        <div className={circleClass}>
          {isCompleted ? <img src={check} alt='체크' /> : step.id}
        </div>
        <div className='pt-0.5'>
          <div className='font-medium text-sm'>{step.title}</div>
          <div className='text-xs text-gray-500 mt-0.5'>{step.description}</div>
        </div>
      </div>
    );
  };

  const renderStep1 = () => (
    <div className='w-full grid gap-6'>
      <InputField
        label='이름'
        value={formData.name}
        onChange={handleChange('name')}
        placeholder='홍길동'
        required
      />

      <InputField
        label='전화번호'
        type='tel'
        value={formData.phone}
        onChange={handleChange('phone')}
        placeholder='010-0000-0000'
        required
      />

      <InputField
        label='이메일'
        type='email'
        value={formData.email}
        onChange={handleChange('email')}
        placeholder='example@email.com'
        required
      />

      <div className='w-full grid grid-cols-1 gap-6 md:grid-cols-2'>
        <Select
          label='성별'
          options={genderOptions}
          value={formData.gender}
          onChange={handleChange('gender')}
          placeholder='남성, 여성, 기타'
        />
        <InputField
          label='생년월일'
          type='date'
          value={formData.birthdate}
          onChange={handleChange('birthdate')}
        />
      </div>

      <Select
        label='최종학력'
        options={educationOptions}
        value={formData.education}
        onChange={handleChange('education')}
        placeholder='최종학력 선택'
      />

      <InputField
        label='학교명'
        type='text'
        value={formData.school}
        onChange={handleChange('school')}
        placeholder='학교명을 입력하세요.'
      />

      <InputField
        label='전공'
        type='text'
        value={formData.major}
        onChange={handleChange('major')}
        placeholder='전공학과를 입력하세요.'
      />
    </div>
  );

  const renderStep2 = () => (
    <div className='rounded-2xl border-[0.2px] border-gray-300 py-6 px-4'>
      <div className='grid grid-cols-3 gap-6 mb-8 h-[430px] overflow-y-scroll p-5'>
        {/* Level 1: Category */}
        <div>
          <h3 className='text-sm font-medium text-gray-700 mb-3'>직무 분야</h3>
          <div className='space-y-2'>
            {Object.keys(roleCategories).map((category) => (
              <button
                key={category}
                type='button'
                onClick={() => {
                  setSelectedCategory(category);
                  setSelectedRole('');
                  setSelectedSubRole('');
                  setFormData((prev) => ({
                    ...prev,
                    roleCategory: category,
                    role: '',
                    subRole: '',
                  }));
                }}
                className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition-colors ${
                  selectedCategory === category
                    ? 'bg-blue-50 text-blue-700 font-medium border border-blue-200'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100 border-2 border-transparent'
                }`}>
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Level 2: Role */}
        <div>
          <h3 className='text-sm font-medium text-gray-700 mb-3'>세부 직무</h3>
          {selectedCategory ? (
            <div className='space-y-2 overflow-y-scroll'>
              {roleCategories[selectedCategory].map((role) => (
                <button
                  key={role}
                  type='button'
                  onClick={() => {
                    setSelectedRole(role);
                    setSelectedSubRole('');
                    setFormData((prev) => ({
                      ...prev,
                      role: role,
                      subRole: '',
                    }));
                  }}
                  className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition-colors ${
                    selectedRole === role
                      ? 'bg-blue-50 text-blue-700 font-medium border border-blue-200'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100 border-2 border-transparent'
                  }`}>
                  {role}
                </button>
              ))}
            </div>
          ) : (
            <p className='text-sm text-gray-400 py-4'>
              먼저 직무 분야를 선택해주세요
            </p>
          )}
        </div>

        {/* Level 3: Sub-role */}
        <div className=''>
          <h3 className='text-sm font-medium text-gray-700 mb-3'>
            상세 포지션
          </h3>
          {selectedRole && subRoles[selectedRole] ? (
            <div className='space-y-2'>
              {subRoles[selectedRole].map((subRole) => (
                <button
                  key={subRole}
                  type='button'
                  onClick={() => {
                    setSelectedSubRole(subRole);
                    setFormData((prev) => ({
                      ...prev,
                      subRole,
                    }));
                  }}
                  className={`w-full text-left px-4 py-2.5 rounded-lg text-sm transition-colors ${
                    selectedSubRole === subRole
                      ? 'bg-blue-50 text-blue-700 font-medium border-2 border-blue-200'
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100 border-2 border-transparent'
                  }`}>
                  {subRole}
                </button>
              ))}
            </div>
          ) : (
            <p className='text-sm text-gray-400 py-4'>
              세부 직무를 먼저 선택해주세요
            </p>
          )}
        </div>
      </div>

      {selectedSubRole && (
        <span className='bg-blue-50 border-blue-200 border text-sm font-semibold text-blue-700 rounded-lg px-3 py-2 mb-6'>
          {selectedSubRole}
        </span>
      )}
    </div>
  );

  const renderStep3 = () => (
    <PdfUpload
      label='PDF 업로드'
      file={formData.portfolioPdf}
      onFileChange={(file) =>
        setFormData((prev) => ({...prev, portfolioPdf: file}))
      }
      onRemove={() => setFormData((prev) => ({...prev, portfolioPdf: null}))}
      required
    />
  );

  const renderStepContent = () => {
    if (currentStep === 1) return renderStep1();
    if (currentStep === 2) return renderStep2();
    return renderStep3();
  };

  // -------------------- 렌더 --------------------

  return (
    <div className='w-full min-h-screen px-15 py-12'>
      {/* 가운데 정렬된 전체 컨테이너 */}
      <div className='max-w-6xl mx-auto flex items-start'>
        {/* Sidebar */}
        <nav className='hidden lg:block mt-30'>
          <h2 className='text-sm font-semibold text-gray-500 uppercase mb-6'>
            지원 단계
          </h2>
          <div className='space-y-4'>
            {STEPS.map((step) => renderSidebarStep(step))}
          </div>
        </nav>

        {/* Main content */}
        <main className='flex-1 max-w-[700px] mx-auto mt-10'>
          {/* Form header */}
          <div className='text-center mb-10'>
            <h1 className='text-3xl font-bold text-blue'>
              {STEP_TITLES[currentStep]}
            </h1>
            <p className='mt-2 text-grey'>{STEP_DESCRIPTIONS[currentStep]}</p>
          </div>

          <form onSubmit={handleSubmit} className='w-full flex flex-col gap-6'>
            {renderStepContent()}

            <div className='flex gap-5 justify-between items-center mt-4'>
              <Button
                type='button'
                variant='ghost'
                className={isLoading ? 'hidden' : ''}
                onClick={handlePrev}
                disabled={isLoading}>
                이전
              </Button>

              {currentStep === 3 ? (
                <Button
                  type='submit'
                  className={
                    isLoading ? 'w-fit p-3 px-4 whitespace-nowrap' : ''
                  }
                  disabled={!isFinalSubmitValid || isLoading}>
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
                <Button type='button' onClick={handleNextStep}>
                  다음
                </Button>
              )}
            </div>
          </form>
        </main>
      </div>
    </div>
  );
};

export default CandidateInfo;
