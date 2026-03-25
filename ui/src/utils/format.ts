export function formatPower(kw: number): string {
  if (Math.abs(kw) < 0.1) {
    return `${Math.round(kw * 1000)} W`;
  }
  return `${kw.toFixed(1)} kW`;
}

export function formatCurrency(amount: number, currency: string): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency || "USD"
  }).format(amount);
}

export function formatPercent(pct: number): string {
  return `${pct.toFixed(1)}%`;
}

export function formatStatValue(value: number | null, unit: string): string {
  if (value === null || Number.isNaN(value)) {
    return "—";
  }
  if (unit === "kW") {
    return formatPower(value);
  }
  if (unit === "%") {
    return `${value.toFixed(1)}%`;
  }
  return `${value.toFixed(2)} ${unit}`.trim();
}
