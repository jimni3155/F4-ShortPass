import React, { useState } from 'react';

const FeedbackLoop = ({ candidateId, initialFeedback, onSaveFeedback }) => {
  const [hrComment, setHrComment] = useState(initialFeedback.hr_comment || '');
  const [isAgreed, setIsAgreed] = useState(initialFeedback.is_reviewed ? initialFeedback.adjusted_score === null : null); // null for unreviewed, true for agreed, false for disagreed
  const [adjustedScore, setAdjustedScore] = useState(initialFeedback.adjusted_score || '');

  const handleSave = () => {
    onSaveFeedback({
      candidateId,
      hrComment,
      isAgreed: isAgreed === true, // explicitly true/false
      adjustedScore: isAgreed === false ? parseInt(adjustedScore, 10) : null,
    });
  };

  return (
    <div className="bg-white shadow rounded-lg p-6 mb-8">
      <h3 className="text-xl font-semibold mb-4">피드백 루프 (HR 담당자 의견)</h3>
      <div className="space-y-4">
        <div>
          <label htmlFor="hrComment" className="block text-sm font-medium text-gray-700 mb-1">
            HR 담당자 의견
          </label>
          <textarea
            id="hrComment"
            rows="4"
            className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="AI 평가에 대한 의견을 자유롭게 작성해주세요."
            value={hrComment}
            onChange={(e) => setHrComment(e.target.value)}
          ></textarea>
        </div>

        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">AI 평가에 동의하십니까?</p>
          <div className="flex items-center space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                className="form-radio text-green-600"
                name="aiAgreement"
                value="agree"
                checked={isAgreed === true}
                onChange={() => {setIsAgreed(true); setAdjustedScore('');}}
              />
              <span className="ml-2">👍 동의함</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                className="form-radio text-red-600"
                name="aiAgreement"
                value="disagree"
                checked={isAgreed === false}
                onChange={() => setIsAgreed(false)}
              />
              <span className="ml-2">👎 동의하지 않음</span>
            </label>
          </div>
        </div>

        {isAgreed === false && (
          <div>
            <label htmlFor="adjustedScore" className="block text-sm font-medium text-gray-700 mb-1">
              점수 조정 (AI 평가 점수 {initialFeedback.current_score}점)
            </label>
            <input
              type="number"
              id="adjustedScore"
              className="w-40 p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="조정 점수"
              value={adjustedScore}
              onChange={(e) => setAdjustedScore(e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              조정된 점수는 모델 재학습 데이터로 활용됩니다.
            </p>
          </div>
        )}

        <div className="text-right">
          <button
            onClick={handleSave}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            피드백 저장
          </button>
        </div>

        <p className="text-sm text-gray-500 mt-4 text-center">
          작성해주신 코멘트는 모델의 재학습(Fine-tuning) 데이터로 활용되어, 다음 채용 시 우리 회사 인재상에 더 최적화됩니다.
        </p>
      </div>
    </div>
  );
};

export default FeedbackLoop;