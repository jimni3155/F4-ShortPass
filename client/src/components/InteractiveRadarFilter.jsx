import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend } from 'recharts';

const InteractiveRadarFilter = ({ filterScores, setFilterScores, competencyLabels }) => {

  const handleSliderChange = (e) => {
    const { name, value } = e.target;
    setFilterScores(prevScores => ({
      ...prevScores,
      [name]: parseInt(value, 10),
    }));
  };

  const data = competencyLabels.map(label => ({
    subject: label,
    value: filterScores[label] || 0,
    fullMark: 100,
  }));

  return (
    <div className="bg-white p-6 rounded-lg shadow-md mb-6 grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <h3 className="text-xl font-bold mb-4">역량 프로필 필터</h3>
        <p className="text-sm text-gray-600 mb-4">
          아래 슬라이더를 조절하여 원하는 최소 역량 프로필을 설정하세요.
          설정된 점수 이상을 받은 지원자만 목록에 표시됩니다.
        </p>
        <div className="space-y-4">
          {competencyLabels.map(label => (
            <div key={label}>
              <label htmlFor={label} className="block text-sm font-medium text-gray-700">{label}</label>
              <div className="flex items-center gap-4">
                <input
                  type="range"
                  id={label}
                  name={label}
                  min="0"
                  max="100"
                  step="5"
                  value={filterScores[label] || 0}
                  onChange={handleSliderChange}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <span className="font-semibold text-blue-700 w-12 text-center">{filterScores[label] || 0}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="w-full h-80">
        <ResponsiveContainer>
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
            <PolarGrid />
            <PolarAngleAxis dataKey="subject" />
            <PolarRadiusAxis angle={30} domain={[0, 100]} />
            <Radar name="필터" dataKey="value" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
            <Legend />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default InteractiveRadarFilter;
