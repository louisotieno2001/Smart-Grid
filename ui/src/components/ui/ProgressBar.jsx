export function ProgressBar({ value, color = "var(--accent)", width = "100%" }) {
  return (
    <div className="bar-track" style={{ width }}>
      <div className="bar-fill" style={{ width: `${value}%`, background: color }} />
    </div>
  );
}
