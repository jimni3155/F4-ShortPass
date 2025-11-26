import { useState } from "react"
import competency from '@mock/sampleCompetency'
import alertTriangle from '@assets/svg/alert-triangle.svg'

// ----------------------------------------------------------------------
// 2. 모달 컴포넌트 정의
// ----------------------------------------------------------------------
export function CompetencyDetailModal({ isOpen, onClose }) {
  if (!isOpen || !competency) return null

  // Helper: 신뢰도 뱃지
  const getConfidenceBadge = (confidence) => {
    const score = confidence || 0
    if (score >= 0.8) return { text: "높은 신뢰도", color: "bg-blue-100 text-blue-700" }
    if (score >= 0.6) return { text: "중간 신뢰도", color: "bg-gray-100 text-gray-700" }
    return { text: "낮은 신뢰도", color: "bg-orange-100 text-orange-700" }
  }

  // Helper: 텍스트 하이라이트
  const highlightQuote = (fullText, quote) => {
    if (!fullText) return ""
    if (!quote) return fullText
    const index = fullText.indexOf(quote)
    if (index === -1) return fullText
    return (
      <>
        {fullText.slice(0, index)}
        <span className="bg-blue-50 border-l-2 font-medium border-blue-400 px-2 py-0.5 rounded mx-1">
          {quote}
        </span>
        {fullText.slice(index + quote.length)}
      </>
    )
  }

  // Helper: 심각도 뱃지
  const getSeverityBadge = (severity) => {
    const styles = {
      minor: "bg-gray-100 text-gray-700",
      moderate: "bg-orange-100 text-orange-700",
      major: "bg-red-100 text-red-700",
    }
    const labels = {
      minor: "경미",
      moderate: "보통",
      major: "심각",
    }
    return { 
      style: styles[severity] || styles.minor, 
      label: labels[severity] || "알 수 없음" 
    }
  }

  // 데이터 구조 분해
  const { competencyDisplayName, overallScore, confidence, perspectives } = competency
  const { evidence, behavioral, critical } = perspectives
  const confidenceBadge = getConfidenceBadge(confidence?.overallConfidence)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div
        className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 shadow-xs flex justify-between items-start z-10">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold text-gray-900">{competencyDisplayName}</h2>
              <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${confidenceBadge.color}`}>
                {confidenceBadge.text} ({Math.round((confidence?.overallConfidence || 0) * 100)}%)
              </span>
            </div>
            <p className="text-sm text-gray-500 mt-1">공통 역량 평가 상세</p>
          </div>
          <div className="text-right pr-8">
            <div className="text-4xl font-bold text-blue-600">{overallScore}</div>
            <div className="text-xs text-gray-400">종합 점수</div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin scrollbar-thumb-gray-200">
          <div className="space-y-8">
            
            {/* 1. Evidence */}
            <section className="space-y-4">
              <div className="flex items-baseline justify-between border-b border-gray-200 pb-2">
                <h3 className="text-lg font-bold text-gray-900">Evidence (발언 근거)</h3>
                <span className="text-xl font-bold text-blue-600">{evidence.score}</span>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700 leading-relaxed">
                <span className="font-semibold text-gray-900 block mb-1">평가 요약</span>
                {evidence.reasoningSummary}
              </div>
              <div className="space-y-4">
                {evidence.details.map((detail) => (
                  <div key={detail.id} className="border border-gray-200 rounded-lg p-4 space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="inline-block px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-semibold">
                        {detail.summary}
                      </span>
                      <span className="text-xs text-gray-400">Segment {detail.segmentId}</span>
                    </div>
                    <div className="bg-gray-50 rounded p-3 text-sm text-gray-600 leading-relaxed">
                      {highlightQuote(detail.fullTranscript, detail.quote)}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* 2. Behavioral */}
            <section className="space-y-4 pt-4">
              <div className="flex items-baseline justify-between border-b border-gray-200 pb-2">
                <h3 className="text-lg font-bold text-gray-900">Behavioral (행동 패턴)</h3>
                <span className="text-xl font-bold text-blue-600">{behavioral.score}</span>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="p-4 bg-white border border-gray-200 rounded-lg">
                   <h4 className="font-semibold text-gray-900 mb-2 text-sm">주요 행동 패턴</h4>
                   <p className="text-sm text-gray-600">{behavioral.patternDescription}</p>
                </div>
                <div className="p-4 bg-white border border-gray-200 rounded-lg">
                   <h4 className="font-semibold text-gray-900 mb-2 text-sm">일관성 분석</h4>
                   <p className="text-sm text-gray-600">{behavioral.consistencyNote}</p>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="font-semibold text-gray-900 text-sm">구체적 사례 분석</h4>
                {behavioral.specificExamples.map((example, idx) => (
                  <div key={idx} className="flex items-start p-3 bg-blue-50/50 rounded-lg border border-blue-100">
                    <div className="flex flex-col">
                      <span className="w-fit px-1.5 py-0.5 bg-white border border-blue-200 text-blue-600 rounded text-xs font-medium mb-1 mr-2">
                        {example.evidenceType}
                      </span>
                      <span className="text-sm text-gray-700">{example.description}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
                <span className="font-semibold block mb-1">종합 의견</span>
                {behavioral.reasoningSummary}
              </div>
            </section>

            {/* 3. Critical */}
            <section className="space-y-4 pt-4">
              <div className="flex items-baseline justify-between border-b border-gray-200 pb-2">
                <h3 className="text-lg font-bold text-gray-900">Critical (Red Flags)</h3>
                <div className="flex items-baseline gap-1">
                  <span className="text-xl font-bold text-red-600">{critical.totalPenalty}</span>
                </div>
              </div>
              <div className="space-y-3">
                {critical.redFlags.map((flag, idx) => {
                  const severityBadge = getSeverityBadge(flag.severity)
                  return (
                    <div key={idx} className="border border-red-200 rounded-lg p-4 bg-red-50/30 flex gap-4">
                      <img src={alertTriangle} className='w-5 h-5' />
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${severityBadge.style}`}>
                            {severityBadge.label}
                          </span>
                         
                        </div>
                        <h4 className="font-semibold text-gray-900 text-sm">
                           {flag.flagType === 'conflict_avoidance' ? '갈등 회피 성향' : 
                            flag.flagType === 'individualism' ? '개인주의적 태도' : flag.flagType}
                        </h4>
                        <p className="text-sm text-gray-700">{flag.description}</p>
                        <p className="text-xs text-gray-400 mt-1">Segment {flag.segmentId} . {flag.penalty}점 감점</p>
                      </div>
                    </div>
                  )
                })}
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
                <span className="font-semibold block mb-1">리스크 요약</span>
                {critical.reasoningSummary}
              </div>
            </section>

          </div>
        </div>

        {/* Footer */}
        <div className="p-4 shadow-sm flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  )
}