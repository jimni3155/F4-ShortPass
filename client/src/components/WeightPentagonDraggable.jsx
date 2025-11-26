import {useCallback, useEffect, useMemo, useRef, useState} from 'react';

const clamp = (val, min, max) => Math.min(Math.max(val, min), max);

/**
 * 오각형 드래그로 역량 가중치를 조정하는 인터랙티브 컴포넌트.
 * - 총합이 2가 되도록 정규화 (평균 0.4)
 */
const WeightPentagonDraggable = ({weights = [], onChange}) => {
  const svgRef = useRef(null);
  const [localWeights, setLocalWeights] = useState(weights);
  const [draggingIndex, setDraggingIndex] = useState(null);

  useEffect(() => {
    setLocalWeights(weights);
  }, [weights]);

  // [수정 1] 총합이 2가 되도록 정규화 로직 변경
  const normalized = useCallback((arr) => {
    const total = arr.reduce((sum, w) => sum + (w.value || 0), 0) || 1;
    // (개별값 / 현재총합) * 목표총합(2)
    return arr.map((w) => ({...w, value: ((w.value || 0) / total) * 2}));
  }, []);

  const updateWeight = useCallback(
    (index, rawValue) => {
      // [수정 2] 합이 2인 경우 한 항목이 1을 넘을 수 있으므로 max clamp를 2로 확장
      const clampedValue = clamp(rawValue, 0.05, 2);
      const next = normalized(
        localWeights.map((w, i) => (i === index ? {...w, value: clampedValue} : w))
      );
      setLocalWeights(next);
      onChange?.(next);
    },
    [localWeights, normalized, onChange]
  );

  const handlePointerMove = useCallback(
    (clientX, clientY) => {
      if (draggingIndex === null || !svgRef.current) return;
      const rect = svgRef.current.getBoundingClientRect();
      const x = clientX - rect.left;
      const y = clientY - rect.top;
      const width = rect.width;
      const height = rect.height;
      const centerX = width / 2;
      const centerY = height / 2;
      const radius = Math.min(width, height) * 0.35;

      const angle = (Math.PI * 2 * draggingIndex) / 5 - Math.PI / 2;
      const dx = x - centerX;
      const dy = y - centerY;

      const projected = dx * Math.cos(angle) + dy * Math.sin(angle);
      // [수정 3] 드래그 시 원 바깥으로 나가면 1.0 이상이 될 수 있도록 max를 2로 설정
      const value = clamp(projected / radius, 0.05, 2);
      updateWeight(draggingIndex, value);
    },
    [draggingIndex, updateWeight]
  );

  useEffect(() => {
    const handlePointerUp = () => setDraggingIndex(null);
    const handleMove = (e) => handlePointerMove(e.clientX, e.clientY);

    if (draggingIndex !== null) {
      window.addEventListener('pointermove', handleMove);
      window.addEventListener('pointerup', handlePointerUp, {once: true});
    }
    return () => {
      window.removeEventListener('pointermove', handleMove);
      window.removeEventListener('pointerup', handlePointerUp);
    };
  }, [draggingIndex, handlePointerMove]);

  const {points, labels, centerX, centerY, radius, width, height} = useMemo(() => {
    const width = 380;
    const height = 380;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;

    const pts = localWeights.map((w, i) => {
      const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      // w.value가 1보다 크면 원 밖으로 그려짐 (의도된 동작)
      const r = radius * (w.value || 0);
      return {
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle),
        angle,
      };
    });

    // 라벨 위치는 그리드보다 조금 더 바깥으로 (혹은 값에 따라 동적으로 밀어낼 수도 있음)
    const labelRadius = radius + 40; 
    const labelPoints = localWeights.map((w, i) => {
      const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      return {
        x: centerX + labelRadius * Math.cos(angle),
        y: centerY + labelRadius * Math.sin(angle),
      };
    });

    return {points: pts, labels: labelPoints, centerX, centerY, radius, width, height};
  }, [localWeights]);

  const renderGrid = () => {
    // 그리드는 여전히 0~1.0(100%) 기준으로 그립니다.
    // 값이 1.0을 넘으면 그리드 밖으로 나가는 것이 "초과 달성" 느낌을 줍니다.
    const levels = [0.2, 0.4, 0.6, 0.8, 1];
    const width = 380;
    const height = 380;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;

    return levels.map((lvl, idx) => {
      const pathPoints = [];
      for (let i = 0; i < 5; i++) {
        const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
        const r = radius * lvl;
        pathPoints.push(`${centerX + r * Math.cos(angle)},${centerY + r * Math.sin(angle)}`);
      }
      const d = `M ${pathPoints.join(' L ')} Z`;
      return <path key={idx} d={d} fill='none' stroke='#e5e7eb' strokeWidth='1' />;
    });
  };

  const polygonPath = useMemo(() => {
    if (!points.length) return '';
    return points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ') + ' Z';
  }, [points]);

  return (
    <div className='w-full flex flex-col gap-4'>
      <div className='text-sm text-gray-700'>
        {/* 안내 문구 업데이트 */}
        오각형 꼭짓점을 드래그해 가중치를 조정하세요. 합은 자동으로 <strong>1</strong>로 정규화됩니다.
      </div>
      <div className='w-full flex flex-col gap-6 items-center mt-5'>
        <svg
          ref={svgRef}
          viewBox='0 0 380 380'
          className='w-full max-w-md touch-none select-none'
          style={{overflow: 'visible'}} // 점이 밖으로 나갈 수 있으므로 visible 추천
        >
          <g>{renderGrid()}</g>

          {/* 축 */}
          <line x1={centerX} y1={centerY} x2={centerX} y2={centerY} stroke='transparent' />
          {points.map((p, i) => {
             // 축 길이는 고정(radius)할지 점을 따라갈지 결정. 여기선 그리드(1.0)까지만 그립니다.
             const axisEndRadius = Math.min(width, height) * 0.35; 
             const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
             return (
              <line
                key={`axis-${i}`}
                x1={centerX}
                y1={centerY}
                x2={centerX + Math.cos(angle) * axisEndRadius}
                y2={centerY + Math.sin(angle) * axisEndRadius}
                stroke='#d1d5db'
                strokeWidth='1'
              />
            )
          })}

          {/* 폴리곤 */}
          <path d={polygonPath} fill='rgba(59,130,246,0.2)' stroke='#3b82f6' strokeWidth='2' />

          {/* 드래그 핸들 */}
          {points.map((p, i) => (
            <g key={`handle-${i}`}>
              <circle
                cx={p.x}
                cy={p.y}
                r={9}
                fill='#1d4ed8'
                className='cursor-pointer'
                onPointerDown={(e) => {
                  e.preventDefault();
                  setDraggingIndex(i);
                }}
              />
              <text
                x={p.x}
                y={p.y - 14}
                textAnchor='middle'
                fontSize='12'
                fill='#0f172a'
                className="font-bold shadow-sm"
              >
                {/* 퍼센트 표시 */}
                {/* {(localWeights[i]?.value * 100).toFixed(0)}% */}
                {(localWeights[i]?.value * 100 / 2).toFixed(0)}%
              </text>
            </g>
          ))}

          {/* 라벨 */}
          {labels.map((pos, i) => (
            <text
              key={`label-${i}`}
              x={pos.x}
              y={pos.y}
              textAnchor='middle'
              fontSize='13'
              fill='#111827'
              fontWeight='700'
            >
              {localWeights[i]?.label || `역량 ${i + 1}`}
            </text>
          ))}
        </svg>

        <div className='flex-1 grid grid-cols-1 sm:grid-cols-2 gap-3 w-full'>
          {localWeights.map((w, idx) => (
            <div key={w.id || idx} className='p-4 rounded-lg border bg-white shadow-sm'>
              <div className='flex justify-between items-center mb-2'>
                <div className='font-semibold text-gray-900'>{w.label || w.id}</div>
                {/* 100%가 넘을 수 있으므로 파란색 강조 */}
                <div className={`font-bold ${w.value > 1 ? 'text-red-600' : 'text-blue-700'}`}>
                  {(w.value * 100 / 2).toFixed(0)}%
                </div>
              </div>
              <div className='w-full bg-gray-200 h-2 rounded-full overflow-hidden'>
                <div
                  className={`h-2 rounded-full ${w.value > 1 ? 'bg-red-500' : 'bg-blue-500'}`}
                  // [수정 4] 100%를 넘는 경우 시각적으로 꽉 차게 보이도록 clamp 처리 (혹은 max를 200%로 잡을 수도 있음)
                  // 여기서는 UI가 깨지지 않도록 100%에서 자릅니다.
                  style={{width: `${clamp(w.value * 100 / 2, 0, 100)}%`}}
                />
              </div>
              <div className='text-xs text-gray-500 mt-1'>
                {w.value > 1 ? '기준치 초과 (강점)' : '드래그로 조정'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WeightPentagonDraggable;