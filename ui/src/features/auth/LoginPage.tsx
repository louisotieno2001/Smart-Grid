import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ErrorBanner } from "../../components/ui/ErrorBanner";
import { useAuth } from "./useAuth";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", background: "#f6f8fb" }}>
      <form
        onSubmit={async (e) => {
          e.preventDefault();
          setError(null);
          setLoading(true);
          try {
            await login(email, password);
            navigate("/sites", { replace: true });
          } catch (err) {
            setError(err as Error);
          } finally {
            setLoading(false);
          }
        }}
        style={{ width: 380, background: "#fff", border: "1px solid #ddd", borderRadius: 10, padding: 18, display: "grid", gap: 10 }}
      >
        <h2 style={{ margin: 0 }}>Login</h2>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" required />
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="password" required />
        <button disabled={loading} type="submit">
          {loading ? "Signing in..." : "Sign in"}
        </button>
        <ErrorBanner error={error} />
      </form>
    </div>
  );
}
