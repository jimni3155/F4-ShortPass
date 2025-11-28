import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from 'recharts';

import candidateDetailMock from '../mock/candidateDetailMock';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const CandidateDetailPage = () => {
  const { jobId, applicantId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('common'); // 'common' | 'job'

  useEffect(() => {
    const mapApiToView = (apiData) => {
      const aggregated = apiData.aggregated_evaluation || {};
      const finalResult = aggregated.final_result || {};
      const analysisSummary = apiData.analysis_summary || aggregated.analysis_summary || {};

      const scores = finalResult.scores || {
        final_score: finalResult.final_score,
        job_overall: finalResult.job_overall,
        common_overall: finalResult.common_overall,
        confidence_overall: finalResult.confidence_overall,
        reliability_level: finalResult.reliability_level,
      };

      const competencies = finalResult.competencies || [];

      return {
        interview_id: apiData.interview_id || finalResult.interview_id,
        applicant_id: apiData.applicant_id,
        applicant_name: apiData.applicant_name || "지원자",
        job_id: apiData.job_id,
        job_title: apiData.job_title || finalResult.job_title || "직무명 미정",
        company_id: apiData.company_id,
        interview_date: apiData.interview_date,
        scores,
        competencies,
        analysis_summary: analysisSummary,
      };
    };

    const fetchDetail = async () => {
      try {
        setLoading(true);

        // mock 모드 지원
        if (jobId === 'mock') {
          setData(candidateDetailMock);
          setLoading(false);
          return;
        }

        const res = await fetch(`${API_BASE}/evaluations/jobs/${jobId}/applicants/${applicantId}/result`);
        if (!res.ok) {
          throw new Error('API 응답 오류');
        }
        const json = await res.json();
        setData(mapApiToView(json));
      } catch (err) {
        console.error('상세 데이터 로드 실패, mock 사용:', err);
        setData(candidateDetailMock);
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
  }, [jobId, applicantId]);

  if (loading) {
    return <div className="flex items-center justify-center h-screen">로딩 중...</div>;
  }

  if (!data) {
    return <div className="flex items-center justify-center h-screen">데이터를 찾을 수 없습니다.</div>;
  }

  // 레이더 차트 데이터 변환 (100점 기준)
  const radarData = activeTab === 'common'
    ? data.competencies.filter(c => c.category === 'common').map(c => ({ name: c.name, score: c.score, fullMark: 100 }))
    : data.competencies.filter(c => c.category === 'job').map(c => ({ name: c.name, score: c.score, fullMark: 100 }));

  const summary = data.analysis_summary || {};

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex justify-between items-start">
            <div>
              <button
                onClick={() => navigate(`/company/applicants/${jobId}`)}
                className="text-gray-500 hover:text-gray-700 text-sm mb-2 flex items-center gap-1"
              >
                ← 목록으로 돌아가기
              </button>
              <h1 className="text-2xl font-bold text-gray-900">지원자 심사평</h1>
              <p className="text-gray-600 mt-1">
                {data.applicant_name} | {data.job_title} | 면접일: {data.interview_date}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">총합 점수</p>
              <p className="text-5xl font-bold text-blue-600">{data.scores?.final_score}</p>
            </div>
          </div>
        </div>

        {/* 메인 콘텐츠 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 좌측: 역량 평가 */}
          <div className="space-y-6">
            {/* 탭 + 레이더 차트 */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              {/* 탭 */}
              <div className="flex border-b mb-4">
                <button
                  onClick={() => setActiveTab('common')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'common'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  공통 역량
                </button>
                <button
                  onClick={() => setActiveTab('job')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'job'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  직무 역량
                </button>
              </div>

              {/* 설명 */}
              <h3 className="font-semibold text-gray-900 mb-1">
                {activeTab === 'common' ? '공통역량 평가' : '직무역량 평가'}
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                {activeTab === 'common'
                  ? 'AI가 면접 답변 기반으로 산출한 공통 역량 점수입니다.'
                  : 'JD 기반 직무 관련 역량 평가 결과입니다.'}
              </p>

              {/* 레이더 차트 */}
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
                    <PolarGrid stroke="#e5e7eb" />
                    <PolarAngleAxis
                      dataKey="name"
                      tick={{ fontSize: 11, fill: '#6b7280' }}
                      tickLine={false}
                    />
                    <PolarRadiusAxis
                      angle={90}
                      domain={[0, 100]}
                      tick={{ fontSize: 10 }}
                      tickCount={6}
                    />
                    <Radar
                      name="점수"
                      dataKey="score"
                      stroke={activeTab === 'common' ? '#ec4899' : '#3b82f6'}
                      fill={activeTab === 'common' ? '#ec4899' : '#3b82f6'}
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 역량별 점수 (막대 그래프) */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex border-b mb-4">
                <span className="px-4 py-2 text-sm font-medium text-gray-500">공통 역량</span>
                <span className="px-4 py-2 text-sm font-medium border-b-2 border-blue-600 text-blue-600">직무 역량</span>
              </div>

              <h3 className="font-semibold text-gray-900 mb-1">직무역량 평가</h3>
              <p className="text-sm text-gray-500 mb-4">JD 기반 직무 관련 5가지 핵심 역량 평가 결과입니다.</p>

              {/* 막대 그래프 */}
              <div className="space-y-3">
                {data.competencies.filter(c => c.category === 'job').map((item, idx) => (
                  <div key={idx} className="flex items-center gap-3">
                    <span className="text-xs text-gray-600 w-48 truncate" title={item.name}>
                      {item.name}
                    </span>
                    <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                      <div
                        className="bg-blue-500 h-2.5 rounded-full transition-all"
                        style={{ width: `${item.score}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-700 w-8">{item.score}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 우측: AI 분석 + 키워드 + 추천질문 */}
          <div className="space-y-6">
            {/* AI 심층 분석 심사평 (지민) */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-3">AI 심층 분석 심사평</h3>
              <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
                {summary.aggregator_summary}
              </div>
            </div>

            {/* 지원 후처리: 전체 요약 + 키워드 */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-2">지원자 전체 요약</h3>
              <p className="text-sm text-gray-700 leading-relaxed mb-4">
                {summary.overall_applicant_summary}
              </p>

              <h3 className="font-semibold text-gray-900 mb-3">요약 평가 키워드</h3>

              {/* 긍정 키워드 */}
              <div className="mb-4">
                <p className="text-sm text-gray-500 mb-2">긍정</p>
                <div className="flex flex-wrap gap-2">
                  {summary.positive_keywords?.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-cyan-50 text-cyan-700 text-xs rounded-full border border-cyan-200"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>

              {/* 부정 키워드 */}
              <div>
                <p className="text-sm text-gray-500 mb-2">부정</p>
                <div className="flex flex-wrap gap-2">
                  {summary.negative_keywords?.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-red-50 text-red-600 text-xs rounded-full border border-red-200"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* 추천 질문 목록 */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="font-semibold text-gray-900 mb-2">추천 질문 목록</h3>
              <p className="text-sm text-gray-500 mb-4">
                지원자의 답변을 바탕으로 AI가 생성한 심화 면접 질문입니다.
              </p>

              <ol className="space-y-3">
                {summary.recommended_questions?.map((question, idx) => (
                  <li key={idx} className="flex gap-3 text-sm text-gray-700">
                    <span className="font-medium text-blue-600 shrink-0">{idx + 1}.</span>
                    <span>{question}</span>
                  </li>
                ))}
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CandidateDetailPage;
