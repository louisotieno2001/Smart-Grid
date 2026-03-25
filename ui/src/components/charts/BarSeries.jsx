export function BarSeries({ values, labels, color = "var(--accent)", height = 90 }) {
  const max = Math.max(...values);
  return (
    <div className="chart-bars" style={{ height }}>
      {values.map((value, index) => (
        <div key={`${labels[index]}-${value}`} className="chart-bar-wrap">
          <div className="chart-bar" style={{ height: `${Math.round((value / max) * (height - 10))}px`, background: color }} />
          <div className="chart-bar-label">{labels[index]}</div>
        </div>
      ))}
    </div>
  );
}
