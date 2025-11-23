const DeepDiveAnalysis = ({ analysisData }) => {
  if (!analysisData || analysisData.length === 0) {
    return <div className="text-center text-gray-500">심층 분석 데이터가 없습니다.</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg p-6 mb-8">
      <h3 className="text-xl font-semibold mb-4">하이라이트 & 꼬리질문 분석 (Evidence)</h3>
      <div className="space-y-8">
        {analysisData.map((item, index) => (
          <div key={index} className="border-b pb-6 last:border-b-0 last:pb-0">
            <p className="text-sm text-gray-500 mb-2">
              <span className="font-semibold">질문 주제:</span> {item.question_topic}
              {item.trigger_reason && <span className="ml-4 text-orange-600">({item.trigger_reason})</span>}
            </p>
            <div className="bg-gray-50 p-4 rounded-lg mb-3">
              <p className="font-medium text-gray-800">Q (초기 질문): {item.initial_question}</p>
              <p className="text-gray-600 mt-1">A (지원자 답변): {item.candidate_initial_response}</p>
            </div>
            {item.follow_up_question && (
              <div className="bg-blue-50 p-4 rounded-lg mb-3 border-l-4 border-blue-400">
                <p className="font-medium text-blue-800"> AI Agent (꼬리질문): {item.follow_up_question}</p>
                <p className="text-blue-700 mt-1">A (지원자 대응 요약): {item.candidate_response_summary}</p>
              </div>
            )}
            <div className="bg-green-50 p-4 rounded-lg mb-3 border-l-4 border-green-400">
                <p className="font-medium text-green-800">평가 코멘트: {item.agent_evaluation}</p>
                {item.score_impact && <p className="text-green-700 mt-1">점수 영향: {item.score_impact}</p>}
            </div>
            {item.transcript_segment_id && (
              <p className="text-gray-500 text-xs mt-2 text-right">
                <span className="font-semibold">대화 세그먼트:</span> {item.transcript_segment_id}
                <button className="ml-2 text-blue-500 hover:underline"> [전체 Transcript 보기] </button>
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default DeepDiveAnalysis;