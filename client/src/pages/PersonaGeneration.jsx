import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import InputField from '../components/InputField';
import PdfUpload from '../components/FileUpload';
import Button from '../components/Button';
import PentagonChart from '../components/PentagonChart';
import WeightPentagonDraggable from '../components/WeightPentagonDraggable';
// import {uploadJDAndAnalyze, generatePersona} from '../apis/jdPersona';
import personaSamsungFashion from '../mock/personaSamsungFashion';

const PersonaGeneration = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: 입력, 2: 역량 확인, 3: 완료

  const [formData, setFormData] = useState({
    companyName: '',
    companyUrl: '',
    jdPdf: null,
    jobTitle: '',
  });

  const [analysisResult, setAnalysisResult] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [competencies, setCompetencies] = useState([]);
  const [weights, setWeights] = useState([]);

  // Step 1: JD 업로드 및 역량 분석
  const handleAnalyze = async () => {
    // MOCK: PDF 없이 바로 persona_samsung_fashion 기반 역량 세팅
    if (!formData.companyName || !formData.jobTitle) {
      alert('회사명과 채용 포지션을 입력해주세요.');
      return;
    }

    setLoading(true);
    try {
      const jobCompetencies =
        personaSamsungFashion.job_competencies?.map((c) => c.name || c.id) ||
        personaSamsungFashion.initial_questions ||
        [];

      const mockResult = {
        job_id: 1,
        common_competencies:
          personaSamsungFashion.common_competencies?.map((c) => c.name || c.id) ||
          ['고객지향', '도전정신', '협동·팀워크', '목표지향', '책임감'],
        job_competencies: jobCompetencies,
        analysis_summary: '삼성물산 패션부문 MD/영업 직무 핵심 역량 분석 (Mock)',
      };

      setAnalysisResult(mockResult);
      setJobId(mockResult.job_id);

      const topFive = jobCompetencies.slice(0, 5).map((comp, index) => ({
        name: comp,
        score: 80 + index * 2,
      }));
      while (topFive.length < 5) {
        topFive.push({name: `역량 ${topFive.length + 1}`, score: 70});
      }

      setCompetencies(topFive);
      const equalWeight = 1 / topFive.length;
      setWeights(
        topFive.map((comp) => ({
          id: comp.name,
          label: comp.name,
          value: equalWeight,
        }))
      );
      setStep(2);
    } catch (err) {
      console.error('❌ 분석 실패:', err);
      alert(`분석 중 오류가 발생했습니다: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: 페르소나 생성
  const handleGeneratePersona = async () => {
    if (!jobId) {
      alert('Job ID가 없습니다.');
      return;
    }

    setLoading(true);
    try {
      // MOCK: 서버 호출 없이 페르소나 준비 완료 처리
      setStep(3);
      setTimeout(() => {
        navigate(`/company/result/${jobId}`, {
          state: {personas: personaSamsungFashion.personas},
        });
      }, 500);
    } catch (err) {
      console.error('❌ 페르소나 생성 실패:', err);
      alert(`페르소나 생성 중 오류가 발생했습니다: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen flex justify-center my-15">
      <div className="w-2/3 flex flex-col mx-auto gap-10">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-4">AI 면접 페르소나 생성</h1>
          <div className="flex justify-center gap-4 mb-8">
            <div className={`px-4 py-2 rounded-full ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}>
              1. JD 업로드
            </div>
            <div className={`px-4 py-2 rounded-full ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}>
              2. 역량 확인
            </div>
            <div className={`px-4 py-2 rounded-full ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-300'}`}>
              3. 페르소나 생성
            </div>
          </div>
        </div>

        {/* Step 1: 입력 폼 */}
        {step === 1 && (
          <div className="flex flex-col gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">기업 정보 입력</h2>

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 mb-6">
                <InputField
                  label="회사명"
                  value={formData.companyName}
                  onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
                  placeholder="예: 테크 스타트업"
                  required
                />
                <InputField
                  label="채용 포지션"
                  value={formData.jobTitle}
                  onChange={(e) => setFormData({ ...formData, jobTitle: e.target.value })}
                  placeholder="예: Senior Product Manager"
                  required
                />
              </div>

              <div className="mb-6">
                <InputField
                  label="기업 웹사이트 URL"
                  value={formData.companyUrl}
                  onChange={(e) => setFormData({ ...formData, companyUrl: e.target.value })}
                  placeholder="https://example.com"
                  type="url"
                />
                <p className="text-sm text-gray-500 mt-2">
                  기업 웹사이트를 분석하여 문화와 가치를 파악합니다
                </p>
              </div>

              <PdfUpload
                label="JD (Job Description) PDF"
                file={formData.jdPdf}
                onFileChange={(file) => setFormData({ ...formData, jdPdf: file })}
                onRemove={() => setFormData({ ...formData, jdPdf: null })}
                required
              />
            </div>

            <div className="flex justify-center gap-4">
              <Button onClick={() => navigate('/')} disabled={loading}>
                이전
              </Button>
              <Button onClick={handleAnalyze} disabled={loading}>
                {loading ? '분석 중...' : '직무 역량 분석'}
              </Button>
            </div>
          </div>
        )}

        {/* Step 2: 역량 확인 */}
        {step === 2 && (
          <div className="flex flex-col gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">추출된 직무 역량 (5개)</h2>
              <p className="text-gray-600 mb-6">
                JD 분석 결과, 다음 5가지 핵심 역량이 필요합니다
              </p>

              <div className="flex justify-center mb-6">
                <PentagonChart competencies={competencies} />
              </div>

              <div className="mb-8">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">가중치 설정 (드래그)</h3>
                  <span className="text-xs text-gray-500">
                    합계 100% · 오각형 꼭짓점 드래그
                  </span>
                </div>
                <WeightPentagonDraggable weights={weights} onChange={setWeights} />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {competencies.map((comp, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-gray-50">
                    <div className="flex justify-between items-center">
                      <span className="font-semibold text-gray-900">{comp.name}</span>
                      <span className="text-blue-600 font-bold">{comp.score}</span>
                    </div>
                    <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${comp.score}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-900 mb-2">다음 단계</h3>
                <p className="text-sm text-gray-700">
                  이 역량을 바탕으로 AI 면접관 페르소나를 자동 생성합니다.
                  페르소나는 JD와 기업 웹사이트를 참고하여 생성됩니다.
                </p>
              </div>
            </div>

            <div className="flex justify-center gap-4">
              <Button
                onClick={() => setStep(1)}
                disabled={loading}
              >
                이전
              </Button>
              <Button onClick={handleGeneratePersona} disabled={loading}>
                {loading ? '페르소나 생성 중...' : '페르소나 생성'}
              </Button>
            </div>
          </div>
        )}

        {/* Step 3: 완료 */}
        {step === 3 && (
          <div className="flex flex-col gap-6 items-center">
            <div className="bg-white p-8 rounded-lg shadow text-center">
              <div className="mb-6">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  페르소나 생성 완료!
                </h2>
                <p className="text-gray-600">
                  AI 면접관 페르소나가 성공적으로 생성되었습니다.
                </p>
              </div>

              <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  잠시 후 결과 페이지로 자동 이동합니다...
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonaGeneration;
