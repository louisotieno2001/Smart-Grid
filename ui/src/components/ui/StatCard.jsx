export function StatCard({ label, value, delta, deltaClass = "neutral", valueStyle }) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={valueStyle}>{value}</div>
      <div className={`stat-delta ${deltaClass}`}>{delta}</div>
    </div>
  );
}
