const SummarySection = ({ candidate }) => {
  return (
    <div className="bg-white shadow rounded-lg p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold">{candidate.name} ({candidate.job_title})</h2>
        <div className="text-right">
          <span className="text-4xl font-extrabold text-blue-600">{candidate.total_score}</span>
          <span className="text-xl font-semibold ml-1">점</span>
          <span className={`text-lg font-bold ml-2 ${candidate.grade === 'S' ? 'text-green-500' : 'text-yellow-500'}`}>({candidate.grade}등급)</span>
        </div>
      </div>
      <div className="border-t border-gray-200 pt-4">
        <h3 className="text-xl font-semibold mb-2">AI 총평</h3>
        <p className="text-gray-700 leading-relaxed">{candidate.ai_summary}</p>
      </div>
    </div>
  );
};

export default SummarySection;