import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import Button from '../components/Button';
import { prepareQuestions } from '../apis/interview';

const COMPANIES = [
  {id: '1', name: '테크스타트업 A', positions: '프론트엔드 개발자'},
  {id: '2', name: '글로벌 IT 기업 B', positions: '풀스택 개발자'},
  {id: '3', name: '핀테크 스타트업 C', positions: '백엔드 개발자'},
  {id: '4', name: '이커머스 플랫폼 D', positions: 'DevOps 엔지니어'},
  {id: '5', name: 'AI 스타트업 E', positions: 'ML 엔지니어'},
  {id: '6', name: '글로벌 IT 기업 F', positions: 'AI 개발자'},
];

const API_BASE = 'http://54.226.166.45:8000'

const InterviewStart = () => {
  const [selectedCompanies, setSelectedCompanies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null); // 에러 상태 추가


  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const startInterview = async () => {
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/v1/interviews/prepare`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          candidateId: "1",
          companyId: "1",
          personaInstanceIds: ["1", "2"],
        }),
      });

      const text = await res.text();
      console.log("prepare status:", res.status);
      console.log("prepare body:", text);

      if (!res.ok) {
        // 여기서 500 + 에러 메시지(detail)가 보일 거야
        return;
      }

      const data = JSON.parse(text);

      // 👉 인터뷰 페이지로 이동하며 websocketUrl 전달
      navigate("/candidate/interview", {
        state: {
          websocketUrl: data.websocketUrl,
          interviewId: data.interviewId,
        },
      });
    } catch (err) {
      console.error("인터뷰 준비 실패", err);
    } finally {
      setLoading(false);
    }
  };


  const handleCompanyToggle = (companyId) => {
    setError(null); // 새로운 선택 시 에러 메시지 초기화
    setSelectedCompanies((prev) => {
      if (prev.includes(companyId)) {
        return prev.filter((id) => id !== companyId);
      } else {
        if (prev.length >= 3) {
          return prev;
        }
        return [...prev, companyId];
      }
    });
  };


  const isValidSelection =
    selectedCompanies.length >= 1 && selectedCompanies.length <= 3;

  return (
    <div className='w-full min-h-screen justify-center my-10'>
      <div className='w-2/3 flex flex-col mx-auto'>
        <div className='space-y-2 text-center py-10'>
          <h1 className='text-3xl font-bold'>지원할 회사를 선택하세요</h1>
          <p className='text-grey'>최소 1개, 최대 3개까지 선택 가능합니다</p>
        </div>

        <div className='mb-4 text-sm font-medium text-grey'>
          총 {COMPANIES.length}개 회사
        </div>

        {/* Company list - 2 columns */}
        <div className='grid gap-4 md:grid-cols-2'>
          {COMPANIES.map((company) => {
            const isSelected = selectedCompanies.includes(company.id);
            const isDisabled = !isSelected && selectedCompanies.length >= 3;

            return (
              <label
                key={company.id}
                className={`flex cursor-pointer items-start gap-4 rounded-lg border p-4 transition-all ${
                  isSelected
                    ? 'border-primary bg-primary/5'
                    : isDisabled
                    ? 'cursor-not-allowed border-gray-200 bg-gray-50 opacity-50'
                    : 'border-gray-300 bg-transparent hover:border-gray-300 hover:bg-primary/5'
                }`}>
                <input
                  type='checkbox'
                  checked={isSelected}
                  onChange={() => handleCompanyToggle(company.id)}
                  disabled={isDisabled}
                  className={`mt-1 w-4 h-4 rounded border border-gray-300 appearance-none checked:border-none checked:bg-dark checked:bg-[url('/src/assets/svg/check.svg')] bg-no-repeat bg-center`}
                />
                <div className='flex-1'>
                  <div className='font-medium text-dark'>{company.name}</div>
                  <div className='mt-1 text-sm text-grey'>
                    {company.positions}
                  </div>
                </div>
              </label>
            );
          })}
        </div>

        {/* Selected companies display */}
        {selectedCompanies.length > 0 && (
          <div className='mt-6 rounded-lg bg-gray-50 p-4'>
            <div className='text-sm font-medium text-dark'>
              선택된 회사 ({selectedCompanies.length}/3)
            </div>
            <div className='mt-2 flex flex-wrap gap-2'>
              {selectedCompanies.map((id) => {
                const company = COMPANIES.find((c) => c.id === id);
                return (
                  <div
                    key={id}
                    className='rounded-full bg-primary px-3 py-1 text-sm font-medium text-white'>
                    {company?.name}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        <div className='my-6 rounded-lg border border-primary/20 bg-primary/5 p-4'>
          <p className='text-sm text-grey'>
            공통 질문 + 회사별 질문으로 구성됩니다. 약 40분 소요
          </p>
        </div>

        <div className='flex gap-3 items-center justify-center'>
          <Button
            onClick={() => navigate('/candidate/info')}
            disabled={isLoading}>
            이전
          </Button>
          <Button
            onClick={() => navigate('/candidate/mock-interview')}
            variant='secondary'
            disabled={!isValidSelection || isLoading}>
            Mock 면접 (텍스트)
          </Button>
          <Button
            onClick={startInterview}
            disabled={!isValidSelection || isLoading}>
            {isLoading ? '준비 중...' : '실제 면접 시작'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default InterviewStart;
