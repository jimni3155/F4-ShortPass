import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import InteractiveRadarFilter from '../components/InteractiveRadarFilter';
import candidateListMock from '../mock/candidateListMock';

const competencyLabels = [
  "Data Insight", 
  "Strategic Solving", 
  "Value Chain", 
  "Marketing", 
  "Stakeholder"
];

const CandidateListPage = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [allApplicants, setAllApplicants] = useState([]);
  const [filteredApplicants, setFilteredApplicants] = useState([]);
  const [companyInfo, setCompanyInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Filtering states
  const [searchTerm, setSearchTerm] = useState('');
  const [minScore, setMinScore] = useState('');
  const [filterScores, setFilterScores] = useState(
    competencyLabels.reduce((acc, label) => ({ ...acc, [label]: 0 }), {})
  );

  useEffect(() => {
    const getEvaluations = async () => {
      try {
        setLoading(true);

        // jobId가 'mock'이면 mock 데이터 사용
        if (jobId === 'mock') {
          setCompanyInfo({
            name: candidateListMock.company_name,
            title: candidateListMock.job_title,
            total_applicants: candidateListMock.total_applicants,
            completed_evaluations: candidateListMock.completed_evaluations,
            average_score: candidateListMock.average_score
          });
          setAllApplicants(candidateListMock.applicants);
          setLoading(false);
          return;
        }

        const response = await fetch(`http://localhost:8000/api/v1/evaluations/jobs/${jobId}/applicants`);
        if (!response.ok) {
          throw new Error('Failed to fetch evaluations for job ' + jobId);
        }
        const data = await response.json();

        // 데이터가 없으면 mock 사용
        if (!data.applicants || data.applicants.length === 0) {
          setCompanyInfo({
            name: candidateListMock.company_name,
            title: candidateListMock.job_title,
            total_applicants: candidateListMock.total_applicants,
            completed_evaluations: candidateListMock.completed_evaluations,
            average_score: candidateListMock.average_score
          });
          setAllApplicants(candidateListMock.applicants);
        } else {
          setCompanyInfo({
            name: data.company_name,
            title: data.job_title,
            total_applicants: data.total_applicants,
            completed_evaluations: data.completed_evaluations,
            average_score: data.average_score
          });
          setAllApplicants(data.applicants);
        }
      } catch (err) {
        // API 실패 시에도 mock 데이터 사용
        console.error('API Error, using mock data:', err);
        setCompanyInfo({
          name: candidateListMock.company_name,
          title: candidateListMock.job_title,
          total_applicants: candidateListMock.total_applicants,
          completed_evaluations: candidateListMock.completed_evaluations,
          average_score: candidateListMock.average_score
        });
        setAllApplicants(candidateListMock.applicants);
      } finally {
        setLoading(false);
      }
    };
    getEvaluations();
  }, [jobId]);

  useEffect(() => {
    let tempApplicants = allApplicants;

    // Filter by search term
    if (searchTerm) {
      tempApplicants = tempApplicants.filter(
        (applicant) =>
          applicant.applicant_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          applicant.strengths.toLowerCase().includes(searchTerm.toLowerCase()) ||
          applicant.weaknesses.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by minimum total score
    if (minScore !== '') {
      const score = parseInt(minScore, 10);
      if (!isNaN(score)) {
        tempApplicants = tempApplicants.filter((applicant) => applicant.total_score >= score);
      }
    }

    // Filter by competency scores
    const isCompetencyFilterActive = Object.values(filterScores).some(score => score > 0);
    if (isCompetencyFilterActive) {
      tempApplicants = tempApplicants.filter(applicant => {
        return competencyLabels.every(label => {
          const applicantScore = applicant.competency_scores.find(s => s.name === label)?.score || 0;
          const filterScore = filterScores[label];
          return applicantScore >= filterScore;
        });
      });
    }

    setFilteredApplicants(tempApplicants);
  }, [searchTerm, minScore, filterScores, allApplicants]);

  if (loading) {
    return <div className="text-center py-10">로딩 중...</div>;
  }

  if (error) {
    return <div className="text-center py-10 text-red-500">에러: {error}</div>;
  }
  
  return (
    <div className="w-full min-h-screen flex justify-center py-10 px-4">
      <div className="w-full max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center">
          {companyInfo.name} - {companyInfo.title}
        </h1>
        <p className="text-lg text-gray-600 mb-6 text-center">지원자 평가 결과</p>
        
        <InteractiveRadarFilter 
          filterScores={filterScores}
          setFilterScores={setFilterScores}
          competencyLabels={competencyLabels}
        />

        <div className="mb-6 flex flex-col md:flex-row justify-between items-center bg-white p-4 rounded-lg shadow">
          <div className="text-sm">
            <p>총 지원자: {companyInfo.total_applicants}명</p>
            <p>평가 완료: {companyInfo.completed_evaluations}명</p>
            <p>평균 점수: {companyInfo.average_score?.toFixed(1)}점</p>
          </div>
          <div className="flex items-center gap-4 mt-4 md:mt-0">
            <p className="text-lg font-semibold">
              필터 결과: <span className="text-blue-600">{filteredApplicants.length}</span>명
            </p>
            <input
              type="text"
              placeholder="이름, 강/약점 검색"
              className="p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <input
              type="number"
              placeholder="최소 총점"
              className="p-2 border rounded-md focus:ring-blue-500 focus:border-blue-500 w-32"
              value={minScore}
              onChange={(e) => setMinScore(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto bg-white shadow-md rounded-lg">
          <table className="min-w-full leading-normal">
            <thead>
              <tr>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  순위
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  이름
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  총점
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  강점
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  약점
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  AI 요약
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  상태
                </th>
                <th className="px-5 py-3 border-b-2 border-gray-200 bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                  상세
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredApplicants.length > 0 ? filteredApplicants.map((applicant) => (
                <tr key={applicant.applicant_id} className="hover:bg-gray-50">
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{applicant.rank}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{applicant.applicant_name}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm font-bold">{applicant.total_score}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm text-green-700">{applicant.strengths}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm text-red-700">{applicant.weaknesses}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{applicant.ai_summary_comment}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">{applicant.status}</td>
                  <td className="px-5 py-5 border-b border-gray-200 bg-white text-sm">
                    <button
                      onClick={() => navigate(`/company/applicants/${jobId}/${applicant.applicant_id}`)}
                      className="text-blue-600 hover:text-blue-900 focus:outline-none focus:underline"
                    >
                      보기
                    </button>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="8" className="text-center py-10">해당 조건의 지원자가 없습니다.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default CandidateListPage;