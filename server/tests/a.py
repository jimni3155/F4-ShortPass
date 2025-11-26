segments = [
    {
        "id": "seg_003",
        "text": "SKU 효율을 73%로 달성하면서",
        "agents": [
            ("md_data_analysis", "MD 데이터 분석", 0.90),
            ("seasonal_strategy_kpi", "시즌 전략 KPI", 0.75),
            ("problem_solving", "문제 해결", 0.85),
        ],
        "type": "A",
        "type_label": "multifaceted",
        "penalty": None,
        "reasoning": "구체적 수치(73%)와 함께 3개 역량이 서로 다른 관점에서 평가. 데이터 분석력, KPI 달성, 문제 해결 과정이 각각 독립적으로 드러남."
    },
    {
        "id": "seg_008",
        "text": "시즌 전환 시점에 재고 리스크를 예측해",
        "agents": [
            ("seasonal_strategy_kpi", "시즌 전략 KPI", 0.75),
            ("value_chain_optimization", "가치사슬 최적화", 0.93),
        ],
        "type": "A",
        "type_label": "multifaceted",
        "penalty": None,
        "reasoning": "시즌 전략과 가치사슬 최적화가 동시에 드러나는 복합적 역량 발휘. 각 역량이 명확히 구분되는 관점에서 평가됨."
    },
    {
        "id": "seg_011",
        "text": "항상 최선을 다해 노력했습니다.",
        "agents": [
            ("achievement_motivation", "성취 동기", 0.82),
            ("growth_potential", "성장 잠재력", 0.75),
        ],
        "type": "B",
        "type_label": "generic",
        "penalty": "-5%",
        "reasoning": "구체적 행동이나 결과 없이 추상적 태도만 언급. 두 역량 모두 동일한 모호한 진술에 의존하여 신뢰도 하락."
    },
]

print("[Stage 2-2] Segment Overlap Analysis")
print("━" * 45)
print(f"► {len(segments)} overlapped segments detected")
print()

for seg in segments:
    print(f"{seg['id']}  \"{seg['text']}\"")
    for eng, kor, conf in seg["agents"]:
        print(f"{seg['id']}  {eng}({kor}): {conf}")
    
    type_str = f"type: {seg['type']} ({seg['type_label']})"
    if seg["penalty"]:
        type_str += f" → confidence {seg['penalty']}"
    print(f"         {type_str}")
    print(f"         reason: {seg['reasoning']}")
    print()

print("━" * 45)

type_a = sum(1 for s in segments if s["type"] == "A")
type_b = sum(1 for s in segments if s["type"] == "B")
type_c = sum(1 for s in segments if s["type"] == "C")

print(f"overlap: {len(segments)} | type_a: {type_a} | type_b: {type_b} | type_c: {type_c}")
print()
print("► confidence adjustment:")
print(f"  achievement_motivation(성취 동기): 0.82 → 0.77")
print(f"  growth_potential(성장 잠재력): 0.75 → 0.70")