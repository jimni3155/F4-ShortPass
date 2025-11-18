import React, {useEffect, useState} from 'react';
import InputField from '../components/InputField';
import PdfUpload from '../components/FileUpload';
import Button from '../components/Button';
import Toggle from '../components/Toggle';
import Select from '../components/Select';
import {useNavigate} from 'react-router-dom';
import {uploadJDAndAnalyze} from '../apis/jdPersona';

const sizeOptions = [
  {id: 0, name: '1-10명'},
  {id: 1, name: '11-50명'},
  {id: 2, name: '51-200명'},
  {id: 3, name: '201-500명'},
  {id: 4, name: '501명 이상'},
];

const CompanyInfo = () => {
  const navigate = useNavigate();
  const [isEditable, setIsEditable] = useState(true);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    size: '',
    jdPdf: null,
    questions: [],
    blind: false,
  });

  const [newQuestion, setNewQuestion] = useState('');
  const [companyId, setCompanyId] = useState(1); // 임시 하드코딩
  const [jobId, setJobId] = useState(null); // JD 업로드 후 받는 Job ID

  useEffect(() => {
    const loadCompany = async () => {
      try {
        const company = await getCompany();
        if (company) {
          setFormData(company);
          setIsEditable(false);
        }
      } catch (err) {
        // No existing company data, start fresh
      }
    };
    loadCompany();
  }, []);

  const handleAddQuestion = () => {
    if (newQuestion.trim()) {
      setFormData({
        ...formData,
        questions: [...formData.questions, newQuestion.trim()],
      });
      setNewQuestion('');
    }
  };

  const handleRemoveQuestion = (index) => {
    setFormData({
      ...formData,
      questions: formData.questions.filter((_, i) => i !== index),
    });
  };

  const handleSave = async () => {
    if (!formData.jdPdf) {
      alert('JD PDF를 업로드해주세요.');
      return;
    }

    setLoading(true);
    try {
      // 1. JD PDF 업로드 및 분석
      console.log('📤 JD 업로드 중...');
      const result = await uploadJDAndAnalyze(
        formData.jdPdf,
        companyId,
        formData.name || 'Untitled Position'
      );

      const uploadedJobId = result.job_id;
      setJobId(uploadedJobId);

      console.log('✅ JD 업로드 완료:', result);
      console.log('회사 정보 저장:', formData);

      alert('JD 업로드가 완료되었습니다. 페르소나 생성 페이지로 이동합니다.');

      // 2. 페르소나 생성 페이지로 이동
      navigate(`/company/persona/${uploadedJobId}`);
    } catch (err) {
      console.error('저장 실패:', err);
      alert(`저장 중 오류가 발생했습니다: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditable(true);
  };

  return (
    <div className='w-full min-h-screen flex justify-center my-15'>
      <div className='w-2/3 flex flex-col mx-auto gap-10'>
        {/* Form header */}
        <h1 className='text-center text-3xl font-bold'>기업 정보 입력</h1>
        <form onSubmit={handleSave} className='w-full flex flex-col gap-6'>
          <div className='w-full grid grid-cols-1 gap-6 md:grid-cols-2'>
            <InputField
              label='회사명'
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              placeholder=''
              required
            />
            <Select
              label='규모'
              options={sizeOptions}
              value={formData.size}
              onChange={(e) => setFormData({...formData, size: e.target.value})}
              placeholder='선택하세요'
            />
          </div>

          <PdfUpload
            label='JD PDF'
            file={formData.jdPdf}
            onFileChange={(file) => setFormData({...formData, jdPdf: file})}
            onRemove={() => setFormData({...formData, jdPdf: null})}
            required
          />

          {/* Question Set Section */}
          <div>
            <h2 className='text-sm font-medium mb-2'>추가 질문 세트</h2>

            {isEditable && (
              <div className='flex gap-2 mb-4'>
                <div className='flex-1'>
                  <InputField
                    value={newQuestion}
                    onChange={(e) => setNewQuestion(e.target.value)}
                    placeholder='질문을 입력하세요'
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddQuestion();
                      }
                    }}
                  />
                </div>
                <Button
                  type='button'
                  onClick={handleAddQuestion}
                  disabled={!newQuestion.trim()}
                  className='rounded-lg text-sm'>
                  추가 +
                </Button>
              </div>
            )}

            <div className='flex flex-col gap-2'>
              {formData.questions.map((question, index) => (
                <div
                  key={index}
                  className='flex items-center gap-3 p-3 bg-gray-100 rounded-lg'>
                  <span className='flex-1 text-sm text-text'>{question}</span>
                  {isEditable && (
                    <button
                      type='button'
                      onClick={() => handleRemoveQuestion(index)}
                      className='text-red-500 hover:text-red-700 text-sm font-medium pr-2 cursor-pointer'>
                      삭제
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Blind Toggle */}
          <div className='border border-gray-300 p-5 rounded-lg'>
            <Toggle
              label='블라인드 채용'
              description='학력, 생년월일, 성별 정보를 숨깁니다'
              checked={formData.blind}
              onChange={(checked) => setFormData({...formData, blind: checked})}
              disabled={!isEditable}
            />
          </div>

          {/* Action Buttons */}
          <div className='flex gap-5 justify-center py-10'>
            <Button onClick={() => navigate('/')} disabled={loading}>
              이전
            </Button>
            {isEditable ? (
              <Button onClick={handleSave} disabled={loading}>
                {loading ? '저장 중...' : '저장'}
              </Button>
            ) : (
              <Button onClick={handleEdit}>수정</Button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default CompanyInfo;
