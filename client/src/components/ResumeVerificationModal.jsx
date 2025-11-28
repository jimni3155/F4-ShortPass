import { useEffect } from "react"
import check_green from '@assets/svg/check_green.svg'
const resume_verification = {
      "verified": true,
      "verification_status": "발견됨",
      "strength": "medium",
      "strength_label": "Medium",
      
      "summary": "해당 답변은 Resume의 Projects 섹션과 부분적으로 연관됩니다.",
      
      "resume_matches": [
        {
          "resume_section": "projects",
          "resume_section_label": "Projects 섹션",
          "matched_content": "고객 리뷰 300개 분석 → '심심하다' 피드백 40% 발견",
          "relevance": "이 문장은 지원자의 고객 리뷰 분석 경험을 보여주며, 이번 답변의 '리뷰 기반 인사이트 도출'과 간접적으로 일치합니다."
        }
      ],
      
      "reasoning": {
        "title": "판단 근거",
        "points": [
          "Resume에는 1,000개 분석이 명시되어 있지 않음",
          "그러나 '리뷰 분석을 기반으로 팀 방향 제시' 경험은 확인됨",
          "따라서 \"직접 일치 X, 간접적 연관 O\"로 판단됨"
        ]
      },
      
      "confidence_factors": {
        "title": "신뢰도 요소",
        "factors": [
          {
            "key": "direct_evidence",
            "label": "직접적 증거",
            "value": false,
            "display": "없음 (간접 근거)"
          },
          {
            "key": "multiple_sources",
            "label": "복수 출처 확인",
            "value": true,
            "display": "있음 (projects 외 다른 문맥도 일치)"
          },
          {
            "key": "time_consistency",
            "label": "시간 일관성",
            "value": true,
            "display": "있음"
          },
          {
            "key": "detail_level",
            "label": "세부 수준",
            "value": "medium",
            "display": "중간(Medium)"
          }
        ]
      }
    }


export default function ResumeVerificationModal({ isOpen, onClose, resumeUrl }) {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape" && isOpen) {
        onClose()
      }
    }
    window.addEventListener("keydown", handleEscape)
    return () => window.removeEventListener("keydown", handleEscape)
  }, [isOpen, onClose])

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = "hidden"
    } else {
      document.body.style.overflow = "unset"
    }
    return () => {
      document.body.style.overflow = "unset"
    }
  }, [isOpen])

  if (!isOpen) return null

  const getStrengthColor = (strength) => {
    switch (strength) {
      case "high":
        return "text-emerald-700 bg-emerald-50"
      case "medium":
        return "text-amber-700 bg-amber-50"
      case "low":
        return "text-rose-700 bg-rose-50"
      default:
        return "text-slate-700 bg-slate-50"
    }
  }

  const handleOpenResume = () => {
    if (resumeUrl) {
      window.open(resumeUrl, "_blank")
    }
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" onClick={handleBackdropClick}>
      <div className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto bg-white rounded-lg shadow-xl">
        <div className="p-6">
          {/* Header Section */}
          <div className="border-b border-slate-200 pb-6 mb-6">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h2 className="text-2xl font-bold text-slate-900 mb-4">이력서 검증 결과</h2>
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 rounded-lg">
                      <img src={check_green} className="w-5 h-5"/>
                      <span className="font-semibold text-emerald-700">{resume_verification.verification_status}</span>
                    </div>
                  <span
                    className={`${getStrengthColor(resume_verification.strength)} font-semibold px-4 py-2 text-sm rounded-lg`}
                  >
                    신뢰도: {resume_verification.strength_label}
                  </span>
                </div>
              </div>
              <button
                onClick={handleOpenResume}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                이력서 보기
              </button>
            </div>
          </div>

          <div className="space-y-8">
            {/* Summary Section */}
            <div>
              <h3 className="font-bold text-slate-900 text-lg mb-3">요약</h3>
              <div className="bg-blue-50 rounded-lg p-5">
                <p className="text-blue-900 leading-relaxed">{resume_verification.summary}</p>
              </div>
            </div>

            <div className="border-t border-slate-200" />

            {/* Resume Matches */}
            {resume_verification.resume_matches && resume_verification.resume_matches.length > 0 && (
              <>
                <div>
                  <h3 className="font-bold text-slate-900 text-lg mb-4">이력서 매칭 내용</h3>
                  <div className="space-y-4">
                    {resume_verification.resume_matches.map((match, index) => (
                      <div key={index} className="pl-4 border-l-2 border-indigo-300">
                        <span className="inline-block text-indigo-700 bg-indigo-50 font-semibold px-3 py-1 mb-3 rounded text-sm">
                          {match.resume_section_label}
                        </span>
                        <p className="text-slate-800 mb-3 leading-relaxed">{match.matched_content}</p>
                        <p className="text-sm text-slate-600 leading-relaxed">
                          <span className="font-semibold">연관성:</span> {match.relevance}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="border-t border-slate-200" />
              </>
            )}

            {/* Reasoning */}
            {resume_verification.reasoning && (
              <>
                <div>
                  <h3 className="font-bold text-slate-900 text-lg mb-4">{resume_verification.reasoning.title}</h3>
                  <div className="bg-amber-50 rounded-lg p-5">
                    <ul className="space-y-2">
                      {resume_verification.reasoning.points.map((point, index) => (
                        <li key={index} className="flex items-start gap-3 text-amber-900">
                          <span className="text-amber-600 font-bold text-lg mt-0.5">•</span>
                          <span className="leading-relaxed">{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="border-t border-slate-200" />
              </>
            )}

            {/* Confidence Factors */}
            {resume_verification.confidence_factors && (
              <div>
                <h3 className="font-bold text-slate-900 text-lg mb-4">
                  {resume_verification.confidence_factors.title}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {resume_verification.confidence_factors.factors.map((factor, index) => (
                    <div key={index}>
                      <div className="text-sm font-semibold text-slate-700 mb-2">{factor.label}</div>
                      <div
                        className={`text-sm font-bold px-4 py-2 rounded-md inline-block ${
                          factor.value === true
                            ? "bg-emerald-100 text-emerald-700"
                            : factor.value === false
                              ? "bg-rose-100 text-rose-700"
                              : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {factor.display}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
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
