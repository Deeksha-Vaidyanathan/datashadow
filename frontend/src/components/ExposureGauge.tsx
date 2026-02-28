type Props = { score: number };

function color(score: number) {
  if (score <= 25) return "var(--success)";
  if (score <= 50) return "var(--warning)";
  return "var(--danger)";
}

export default function ExposureGauge({ score }: Props) {
  const pct = Math.min(100, Math.max(0, score));
  const c = color(score);
  return (
    <div className="gauge">
      <div className="gauge-ring">
        <div
          className="gauge-fill"
          style={{
            background: `conic-gradient(${c} ${pct * 3.6}deg, var(--border) 0deg)`,
          }}
        />
        <div className="gauge-inner">
          <span className="gauge-value" style={{ color: c }}>
            {score.toFixed(0)}
          </span>
          <span className="gauge-label">Exposure score</span>
        </div>
      </div>
    </div>
  );
}
