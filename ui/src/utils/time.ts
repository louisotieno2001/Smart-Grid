export function formatTimestamp(iso: string): string {
  const d = new Date(iso);
  return `${d.toLocaleString("en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
    timeZone: "UTC"
  })} UTC`;
}

export function formatRelativeTime(iso: string): string {
  const now = Date.now();
  const ts = new Date(iso).getTime();
  const diffSec = Math.floor((now - ts) / 1000);
  if (diffSec < 60) return `${diffSec}s ago`;
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)} min ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)} h ago`;
  return `${Math.floor(diffSec / 86400)} d ago`;
}

export function isStale(iso: string, thresholdSeconds: number): boolean {
  const ts = new Date(iso).getTime();
  const now = Date.now();
  return now - ts > thresholdSeconds * 1000;
}
