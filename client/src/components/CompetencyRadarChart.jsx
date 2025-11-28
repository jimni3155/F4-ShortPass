// Placeholder for a more complex charting library like Chart.js or Recharts
// For now, it will just display text representation.
const CompetencyRadarChart = ({ data }) => {
  if (!data || !data.labels || !data.scores || data.labels.length === 0) {
    return <div className="text-center text-gray-500">역량 데이터를 불러올 수 없습니다.</div>;
  }

  return (
    <div className="bg-white shadow rounded-lg p-6 mb-8">
      <h3 className="text-xl font-semibold mb-4">역량 분석 (레이더 차트)</h3>
      <div className="flex flex-wrap gap-4 justify-center">
        {data.labels.map((label, index) => (
          <div key={label} className="flex flex-col items-center p-3 border rounded-lg">
            <span className="text-sm font-medium text-gray-600">{label}</span>
            <span className="text-lg font-bold text-blue-700">{data.scores[index]}</span>
          </div>
        ))}
      </div>
      <p className="text-sm text-gray-500 mt-4 text-center">
        (실제 구현 시 레이더 차트 라이브러리 연동 예정)
      </p>
    </div>
  );
};

export default CompetencyRadarChart;