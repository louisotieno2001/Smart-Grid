import { Icon } from "../../lib/icons";
import { Badge } from "../ui/Badge";

export function Sidebar({ navItems, page, setPage }) {
  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#000" strokeWidth="2.5" strokeLinecap="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
          </svg>
        </div>
        <div>
          <div className="logo-text">EnergyIQ</div>
          <div className="logo-sub">v1.0.0</div>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "8px 0" }}>
        {navItems.map((item) => (
          <div key={item.id}>
            {item.showSection ? <div className="sidebar-section">{item.section}</div> : null}
            <div className={`nav-item ${page === item.id ? "active" : ""}`} onClick={() => setPage(item.id)}>
              <Icon name={item.icon} size={14} />
              {item.label}
              {item.id === "alerts" ? <Badge tone="red" style={{ marginLeft: "auto", fontSize: 9, padding: "1px 5px" }}>4</Badge> : null}
            </div>
          </div>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="env-badge">
          <div className="env-dot" />
          <span>dev · localhost:5173</span>
        </div>
        <div style={{ marginTop: 8, display: "flex", gap: 6 }}>
          <div style={{ width: 28, height: 28, borderRadius: "50%", background: "var(--surface)", border: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 700, color: "var(--accent)" }}>JO</div>
          <div>
            <div style={{ fontSize: 12, fontWeight: 600 }}>Jerry Onyango</div>
            <div style={{ fontSize: 10, color: "var(--muted)", fontFamily: "var(--mono)" }}>client_admin</div>
          </div>
        </div>
      </div>
    </nav>
  );
}
