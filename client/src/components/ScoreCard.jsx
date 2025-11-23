const ScoreCard = ({ competencyDetails }) => {
  if (!competencyDetails || competencyDetails.length === 0) {
    return <div className="text-center text-gray-500">상세 역량 평가가 없습니다.</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg p-6 mb-8">
      <h3 className="text-xl font-semibold mb-4">상세 역량 스코어 카드</h3>
      <div className="space-y-6">
        {competencyDetails.map((comp) => (
          <div key={comp.name} className="border-b pb-4 last:border-b-0 last:pb-0">
            <div className="flex justify-between items-center mb-2">
              <h4 className="text-lg font-medium">{comp.name}</h4>
              <span className="text-xl font-bold text-purple-700">{comp.score}</span>
            </div>
            {comp.positive_feedback && (
              <p className="text-green-700 text-sm">
                <span className="font-semibold">강점:</span> {comp.positive_feedback}
              </p>
            )}
            {comp.negative_feedback && (
              <p className="text-red-700 text-sm">
                <span className="font-semibold">개선 필요:</span> {comp.negative_feedback}
              </p>
            )}
            {comp.evidence_transcript_id && (
              <p className="text-gray-500 text-xs mt-1">
                <span className="font-semibold">근거:</span> {comp.evidence_transcript_id}
                <button className="ml-2 text-blue-500 hover:underline"> [근거 대화 보기] </button>
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ScoreCard;