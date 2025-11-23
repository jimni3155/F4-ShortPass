import {useCallback, useEffect, useMemo, useRef, useState} from 'react';

const clamp = (val, min, max) => Math.min(Math.max(val, min), max);

/**
 * 오각형 드래그로 역량 가중치를 조정하는 인터랙티브 컴포넌트.
 * - 각 꼭짓점은 한 역량에 매핑
 * - 드래그 시 가중치는 0~1 사이 값으로 업데이트되고 합이 1이 되도록 정규화
 */
const WeightPentagonDraggable = ({weights = [], onChange}) => {
  const svgRef = useRef(null);
  const [localWeights, setLocalWeights] = useState(weights);
  const [draggingIndex, setDraggingIndex] = useState(null);

  useEffect(() => {
    setLocalWeights(weights);
  }, [weights]);

  const normalized = useCallback((arr) => {
    const total = arr.reduce((sum, w) => sum + (w.value || 0), 0) || 1;
    return arr.map((w) => ({...w, value: (w.value || 0) / total}));
  }, []);

  const updateWeight = useCallback(
    (index, rawValue) => {
      const clampedValue = clamp(rawValue, 0.05, 1);
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

      // 축 방향으로만 투영하여 비틀림 없이 반지름 비율 계산
      const projected = dx * Math.cos(angle) + dy * Math.sin(angle);
      const value = clamp(projected / radius, 0.05, 1);
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
      const r = radius * (w.value || 0);
      return {
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle),
        angle,
      };
    });

    const labelRadius = radius + 32;
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
        오각형 꼭짓점을 드래그해 가중치를 조정하세요. 합은 자동으로 1로 정규화됩니다.
      </div>
      <div className='w-full flex flex-col md:flex-row gap-6 items-center'>
        <svg
          ref={svgRef}
          viewBox='0 0 380 380'
          className='w-full max-w-md border border-gray-200 rounded-xl bg-white shadow-sm touch-none select-none'
        >
          <g>{renderGrid()}</g>

          {/* 축 */}
          <line x1={centerX} y1={centerY} x2={centerX} y2={centerY} stroke='transparent' />
          {points.map((p, i) => (
            <line
              key={`axis-${i}`}
              x1={centerX}
              y1={centerY}
              x2={centerX + Math.cos(p.angle) * Math.min(width, height) * 0.35}
              y2={centerY + Math.sin(p.angle) * Math.min(width, height) * 0.35}
              stroke='#d1d5db'
              strokeWidth='1'
            />
          ))}

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
              >
                {(localWeights[i]?.value * 100).toFixed(0)}%
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
                <div className='text-blue-700 font-bold'>{(w.value * 100).toFixed(0)}%</div>
              </div>
              <div className='w-full bg-gray-200 h-2 rounded-full overflow-hidden'>
                <div
                  className='h-2 bg-blue-500 rounded-full'
                  style={{width: `${clamp(w.value * 100, 0, 100)}%`}}
                />
              </div>
              <div className='text-xs text-gray-500 mt-1'>드래그로 조정</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WeightPentagonDraggable;
