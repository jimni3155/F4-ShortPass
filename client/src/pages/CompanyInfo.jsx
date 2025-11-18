import React, {useEffect, useState} from 'react';
import InputField from '../components/InputField';
import PdfUpload from '../components/FileUpload';
import Button from '../components/Button';
import Toggle from '../components/Toggle';
import Select from '../components/Select';
import {useNavigate} from 'react-router-dom';
import {uploadPersonaPdf, getPersonasByCompany} from '../apis/persona';

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
    personaPdf: null,
    questions: [],
    blind: false,
  });

  const [newQuestion, setNewQuestion] = useState('');
  const [personaUploadStatus, setPersonaUploadStatus] = useState(null);
  const [companyId, setCompanyId] = useState(null);
  const [personas, setPersonas] = useState([]);

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
    setLoading(true);
    try {
      // TODO: saveCompany 함수 구현 필요
      // await saveCompany(formData);
      // setToast({message: '저장되었습니다.', type: 'success'});

      // 임시: 회사 ID를 1로 설정 (실제로는 saveCompany에서 반환된 ID 사용)
      const tempCompanyId = 1;
      setCompanyId(tempCompanyId);

      console.log('회사 정보 저장:', formData);
      alert('저장되었습니다. 결과 페이지로 이동합니다.');

      // 저장 후 회사 결과 페이지로 이동 (jobId로 tempCompanyId 사용)
      navigate(`/company/result/${tempCompanyId}`);
    } catch (err) {
      // setToast({message: '저장 중 오류가 발생했습니다.', type: 'error'});
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handlePersonaUpload = async () => {
    if (!formData.personaPdf) {
      alert('페르소나 PDF 파일을 선택해주세요.');
      return;
    }

    if (!companyId) {
      alert('먼저 회사 정보를 저장해주세요.');
      return;
    }

    setLoading(true);
    setPersonaUploadStatus('업로드 중...');

    try {
      const result = await uploadPersonaPdf(companyId, formData.personaPdf);
      setPersonaUploadStatus(
        `✓ 페르소나 생성 완료! ${result.questions.length}개의 질문이 추출되었습니다.`
      );

      // 페르소나 목록 새로고침
      const personaList = await getPersonasByCompany(companyId);
      setPersonas(personaList.personas);

      console.log('생성된 페르소나:', result);
      alert(result.message);
    } catch (err) {
      setPersonaUploadStatus(`✗ 업로드 실패: ${err.message}`);
      alert(`페르소나 업로드 실패: ${err.message}`);
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

          {/* Persona PDF Upload Section */}
          <div className='border border-blue-300 p-5 rounded-lg bg-blue-50'>
            <h2 className='text-lg font-semibold mb-4 text-blue-900'>
              페르소나 생성 (PDF 업로드)
            </h2>
            <p className='text-sm text-gray-600 mb-4'>
              면접관 페르소나를 생성하기 위한 질문 PDF를 업로드하세요. PDF에서
              질문을 자동으로 추출하여 페르소나를 생성합니다.
            </p>

            <PdfUpload
              label='페르소나 질문 PDF'
              file={formData.personaPdf}
              onFileChange={(file) =>
                setFormData({...formData, personaPdf: file})
              }
              onRemove={() => setFormData({...formData, personaPdf: null})}
            />

            <div className='mt-4 flex gap-3 items-center'>
              <Button
                type='button'
                onClick={handlePersonaUpload}
                disabled={loading || !formData.personaPdf || !companyId}
                className='bg-blue-600 hover:bg-blue-700'>
                페르소나 생성
              </Button>
              {personaUploadStatus && (
                <span className='text-sm text-gray-700'>
                  {personaUploadStatus}
                </span>
              )}
            </div>

            {/* 생성된 페르소나 목록 */}
            {personas.length > 0 && (
              <div className='mt-6'>
                <h3 className='text-md font-semibold mb-3 text-blue-900'>
                  생성된 페르소나 ({personas.length}개)
                </h3>
                <div className='flex flex-col gap-3'>
                  {personas.map((persona) => (
                    <div
                      key={persona.id}
                      className='p-4 bg-white rounded-lg border border-blue-200 shadow-sm'>
                      <div className='flex justify-between items-start'>
                        <div className='flex-1'>
                          <h4 className='font-semibold text-gray-900'>
                            {persona.persona_name}
                          </h4>
                          <p className='text-sm text-gray-600 mt-1'>
                            {persona.description}
                          </p>
                          <div className='mt-2 flex gap-2 items-center'>
                            <span className='text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded'>
                              {persona.archetype}
                            </span>
                            {persona.focus_keywords &&
                              persona.focus_keywords.length > 0 && (
                                <span className='text-xs text-gray-500'>
                                  키워드: {persona.focus_keywords.join(', ')}
                                </span>
                              )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

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
