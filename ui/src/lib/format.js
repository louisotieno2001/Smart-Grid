export const fmt = (n) => new Intl.NumberFormat("en-DE", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
}).format(n * 1000);

export const fmtK = (n) => `€${n}K`;
export const pct = (a, b) => Math.round((a / b) * 100);
