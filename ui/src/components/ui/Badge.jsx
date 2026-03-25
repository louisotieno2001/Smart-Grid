export function Badge({ tone = "dim", children, dot = false, style }) {
  return (
    <span className={`badge badge-${tone}`} style={style}>
      {dot ? <span className="badge-dot" /> : null}
      {children}
    </span>
  );
}

export function DriftBadge({ value }) {
  if (value === "stable") return <Badge tone="green" dot>stable</Badge>;
  if (value === "minor") return <Badge tone="amber" dot>minor drift</Badge>;
  if (value === "watch") return <Badge tone="red" dot>watch</Badge>;
  return <Badge>{value}</Badge>;
}

export function StatusBadge({ value }) {
  const map = {
    active: ["green", "live"],
    new: ["blue", "onboarding"],
    accepted: ["blue", "accepted"],
    implemented: ["green", "implemented"],
    open: ["amber", "open"],
    acknowledged: ["blue", "ack'd"],
    investigating: ["amber", "investigating"],
  };
  const [tone, label] = map[value] || ["dim", value];
  return <Badge tone={tone}>{label}</Badge>;
}

export function SeverityBadge({ value }) {
  if (value === "critical") return <Badge tone="red">critical</Badge>;
  if (value === "high") return <Badge tone="amber">high</Badge>;
  if (value === "warning") return <Badge tone="blue">warning</Badge>;
  return <Badge>info</Badge>;
}
