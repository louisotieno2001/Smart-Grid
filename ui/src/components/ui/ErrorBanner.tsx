import React from "react";
import { ApiError } from "../../api/client";

type ErrorBannerProps = {
  error: Error | ApiError | null;
  onRetry?: () => void;
};

export function ErrorBanner({ error, onRetry }: ErrorBannerProps) {
  if (!error) return null;
  const detail = error instanceof ApiError ? error.detail : undefined;
  return (
    <div style={{ border: "1px solid #ffcdd2", background: "#ffebee", color: "#b71c1c", borderRadius: 8, padding: 12 }}>
      <strong>Error:</strong> {error.message}
      {import.meta.env.DEV && detail ? (
        <pre style={{ marginTop: 8, whiteSpace: "pre-wrap", fontSize: 12 }}>{JSON.stringify(detail, null, 2)}</pre>
      ) : null}
      {onRetry ? (
        <div style={{ marginTop: 8 }}>
          <button onClick={onRetry}>Retry</button>
        </div>
      ) : null}
    </div>
  );
}
