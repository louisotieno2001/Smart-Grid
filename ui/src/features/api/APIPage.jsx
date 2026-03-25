import { useMemo, useState } from "react";
import { API_ENDPOINTS } from "../../mocks/data";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";

export default function APIPage() {
  const [tag, setTag] = useState("All");
  const tags = ["All", ...new Set(API_ENDPOINTS.map((endpoint) => endpoint.tag))];
  const filtered = useMemo(() => tag === "All" ? API_ENDPOINTS : API_ENDPOINTS.filter((endpoint) => endpoint.tag === tag), [tag]);

  return (
    <div className="content fade-in">
      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-title">API REFERENCE</div>
        <div className="two-col" style={{ gap: 24 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, fontFamily: "var(--mono)", fontSize: 12 }}>
            {[
              ["Version", "1.0.0"],
              ["Base URL", "https://api.energyallocation.com"],
              ["Auth", "OAuth2 — client credentials"],
              ["Pagination", "cursor-based, max 200/page"],
              ["Idempotency", "Idempotency-Key required on POST"],
              ["Async", "202 Accepted → poll job_id"],
            ].map(([label, value]) => (
              <div key={label} style={{ display: "flex", gap: 12, padding: "6px 0", borderBottom: "1px solid var(--border)" }}>
                <div style={{ minWidth: 120, color: "var(--muted)" }}>{label}</div>
                <div>{value}</div>
              </div>
            ))}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {[
              ["client_admin", "Manage client-level resources"],
              ["facility_manager", "Manage facility operations"],
              ["energy_analyst", "Read analytics and model outputs"],
              ["viewer", "Read-only access"],
              ["ops_admin", "Internal operations access"],
              ["ml_engineer", "Internal ML administration"],
            ].map(([scope, desc]) => (
              <div key={scope} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: 12, padding: "5px 0", borderBottom: "1px solid var(--border)" }}>
                <code style={{ fontFamily: "var(--mono)", fontSize: 11, background: "var(--bg3)", padding: "2px 7px", borderRadius: 4, color: "var(--accent)" }}>{scope}</code>
                <div style={{ color: "var(--muted)" }}>{desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {tags.map((item) => (
          <Button key={item} tone={tag === item ? "accent" : "default"} size="sm" onClick={() => setTag(item)}>{item}</Button>
        ))}
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {filtered.map((endpoint) => (
          <div key={`${endpoint.method}-${endpoint.path}`} className="endpoint-block">
            <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
              <span className={`method method-${endpoint.method.toLowerCase()}`}>{endpoint.method}</span>
              <span className="endpoint-path">{endpoint.path}</span>
              <span style={{ marginLeft: "auto" }}><Badge>{endpoint.tag}</Badge></span>
            </div>
            <div className="endpoint-desc">{endpoint.desc}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
