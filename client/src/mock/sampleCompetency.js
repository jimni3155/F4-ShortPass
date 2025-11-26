const competency = {
    competencyKey: "interpersonal_skill",
    competencyDisplayName: "대인관계 역량",
    overallScore: 62,
    confidence: {
      overallConfidence: 0.68,
      internalConsistency: 0.97,
    },
    perspectives: {
      evidence: {
        score: 67,
        reasoningSummary:
          "데이터 기반 설득 사례는 있으나, 갈등 해결 복잡도가 낮고 경청 및 이해 노력 측면에서 아쉬움이 있어 Fair 구간 상단으로 평가했습니다.",
        details: [
          {
            id: "ev1",
            summary: "커뮤니케이션 (명확한 전달)",
            quote:
              "디자인팀에서 반대가 있었습니다. '브랜드가 평범해진다'고 하셨는데, 저는 데이터를 보여드렸습니다.",
            fullTranscript:
              "네, 디자인팀에서 반대가 있었습니다. '브랜드가 평범해진다'고 하셨는데, 저는 데이터를 보여드렸습니다. 고객 리뷰 분석 결과 '입을 데가 없다'는 피드백이 40%였거든요. 숫자가 명확하니까 결국 제 안대로 진행됐습니다. 디자인팀 의견도 일부 반영은 했지만, 핵심 방향은 제가 제시한 대로 갔고 결과적으로 판매율이 올랐으니 제 판단이 맞았던 거죠.",
            segmentId: 5,
          },
          {
            id: "ev2",
            summary: "갈등 해결 (에스컬레이션 의존)",
            quote:
              "끝까지 반대했다면... 솔직히 팀장님께 말씀드려서 위에서 결정해달라고 했을 것 같습니다.",
            fullTranscript:
              "끝까지 반대했다면... 솔직히 팀장님께 말씀드려서 위에서 결정해달라고 했을 것 같습니다. 데이터가 명확한데 계속 반대하는 건 감정적인 거라고 생각하거든요. 저는 숫자로 증명했으니까 윗선에서 판단해주시면 따르겠죠. 실제로 그렇게 해결된 적도 있었습니다.",
            segmentId: 6,
          },
        ],
      },
      behavioral: {
        score: 64,
        patternDescription: "일부 상황에서 경청하나, 갈등 상황에서는 회피 성향을 보임",
        specificExamples: [
          {
            description: "일부 상황에서 경청 (3개 중 1개 프로젝트에서 타 의견 수용)",
            evidenceType: "경청",
          },
          {
            description:
              "갈등 상황에서 '위에서 결정해달라'며 책임을 상위에 전가하는 패턴",
            evidenceType: "갈등 회피",
          },
        ],
        consistencyNote: "상황에 따라 소통 방식이 달라 일관성이 부족한 편입니다.",
        reasoningSummary:
          "경청과 협업 의식은 일부 드러나지만, 갈등을 직접 다루기보다 에스컬레이션에 의존하는 모습이 반복되어 60–74점 구간으로 평가했습니다.",
      },
      critical: {
        totalPenalty: -8,
        redFlags: [
          {
            flagType: "conflict_avoidance",
            description:
              "Segment 6에서 '위에서 결정해달라'며 갈등 해결을 상위 의사결정에만 의존하는 모습",
            severity: "minor",
            penalty: -3,
            segmentId: 6,
          },
          {
            flagType: "individualism",
            description:
              "Segment 5에서 '결국 제 안대로 진행됐습니다' 등 개인 성과를 강조하는 표현이 반복됨",
            severity: "moderate",
            penalty: -5,
            segmentId: 5,
          },
        ],
        reasoningSummary:
          "직접적인 적대적 행동은 없으나, 갈등 회피 및 개인주의적 태도가 누적되어 총 -8점의 감점을 적용했습니다.",
      },
    },
  }

  export default competency;