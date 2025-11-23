import { useEffect, useRef } from 'react';

const PentagonChart = ({ competencies }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!competencies || competencies.length !== 5) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 140;
    const maxScore = 100;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background grid (concentric pentagons)
    const drawPentagon = (r, color, lineWidth) => {
      ctx.beginPath();
      for (let i = 0; i < 5; i++) {
        const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
        const x = centerX + r * Math.cos(angle);
        const y = centerY + r * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.closePath();
      ctx.strokeStyle = color;
      ctx.lineWidth = lineWidth;
      ctx.stroke();
    };

    // Draw grid lines (5 levels)
    for (let i = 1; i <= 5; i++) {
      drawPentagon((radius * i) / 5, '#e5e7eb', 1);
    }

    // Draw axis lines from center to vertices
    ctx.strokeStyle = '#d1d5db';
    ctx.lineWidth = 1;
    for (let i = 0; i < 5; i++) {
      const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(x, y);
      ctx.stroke();
    }

    // Draw competency scores
    ctx.beginPath();
    competencies.forEach((comp, i) => {
      const score = comp.score || 0;
      const r = (radius * score) / maxScore;
      const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.closePath();
    ctx.fillStyle = 'rgba(59, 130, 246, 0.3)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)';
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw points
    competencies.forEach((comp, i) => {
      const score = comp.score || 0;
      const r = (radius * score) / maxScore;
      const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      const x = centerX + r * Math.cos(angle);
      const y = centerY + r * Math.sin(angle);

      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#3b82f6';
      ctx.fill();
    });

    // Draw labels
    ctx.font = 'bold 14px sans-serif';
    ctx.fillStyle = '#1f2937';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    competencies.forEach((comp, i) => {
      const angle = (Math.PI * 2 * i) / 5 - Math.PI / 2;
      const labelRadius = radius + 30;
      const x = centerX + labelRadius * Math.cos(angle);
      const y = centerY + labelRadius * Math.sin(angle);

      // Draw label background
      const text = comp.name || `역량 ${i + 1}`;
      const textWidth = ctx.measureText(text).width;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.fillRect(x - textWidth / 2 - 8, y - 10, textWidth + 16, 20);

      // Draw label text
      ctx.fillStyle = '#1f2937';
      ctx.fillText(text, x, y);

      // Draw score
      ctx.font = '12px sans-serif';
      ctx.fillStyle = '#6b7280';
      ctx.fillText(`${comp.score}`, x, y + 16);
    });
  }, [competencies]);

  return (
    <div className="flex flex-col items-center">
      <canvas
        ref={canvasRef}
        width={400}
        height={400}
        className="border border-gray-200 rounded-lg bg-white"
      />
    </div>
  );
};

export default PentagonChart;
