import { useState } from "react";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Collapsible } from "../../components/ui/Collapsible";

const MOCK_PARTNERS = [
  {
    id: "ptn_001",
    name: "EnergyTech Solutions",
    status: "active",
    industry: "SaaS Platform",
    apiKeysCount: 3,
    allocationsCount: 2,
    lastActivity: "2 minutes ago",
    webhook: true,
    plan: "Growth",
  },
  {
    id: "ptn_002",
    name: "Industrial Analytics Corp",
    status: "active",
    industry: "Consulting",
    apiKeysCount: 1,
    allocationsCount: 5,
    lastActivity: "1 hour ago",
    webhook: true,
    plan: "Enterprise",
  },
  {
    id: "ptn_003",
    name: "Green Systems Ltd",
    status: "pending",
    industry: "Energy Management",
    apiKeysCount: 0,
    allocationsCount: 0,
    lastActivity: "Never",
    webhook: false,
    plan: "Starter",
  },
  {
    id: "ptn_004",
    name: "Manufacturing Insights",
    status: "active",
    industry: "Data Analytics",
    apiKeysCount: 2,
    allocationsCount: 1,
    lastActivity: "3 hours ago",
    webhook: true,
    plan: "Growth",
  },
];

const MOCK_AUDIT_LOG = [
  { timestamp: "2026-03-24 14:32:15", action: "api_key.created", partner: "EnergyTech Solutions", details: "New key: key_51d3..." },
  { timestamp: "2026-03-24 14:15:00", action: "webhook.updated", partner: "Industrial Analytics Corp", details: "URL changed" },
  { timestamp: "2026-03-24 13:48:22", action: "partner.registered", partner: "Green Systems Ltd", details: "Account created" },
  { timestamp: "2026-03-24 13:20:10", action: "allocation.created", partner: "Manufacturing Insights", details: "Client assignment" },
  { timestamp: "2026-03-24 12:55:33", action: "api_key.rotated", partner: "EnergyTech Solutions", details: "Routine rotation" },
];

export default function PartnerDashboardPage() {
  const [showNewPartnerForm, setShowNewPartnerForm] = useState(false);
  const [expandedPartner, setExpandedPartner] = useState(null);
  
  const activePartners = MOCK_PARTNERS.filter(p => p.status === "active").length;
  const totalAllocations = MOCK_PARTNERS.reduce((sum, p) => sum + p.allocationsCount, 0);
  const totalApiKeys = MOCK_PARTNERS.reduce((sum, p) => sum + p.apiKeysCount, 0);

  return (
    <div className="content fade-in">
      <div className="card" style={{ marginBottom: 14, padding: 12 }}>
        <div style={{ display: "flex", gap: 18, flexWrap: "wrap", fontSize: 12, color: "var(--muted)" }}>
          <span>Active partners: <strong style={{ color: "var(--text)" }}>{activePartners}</strong></span>
          <span>Total registered: <strong style={{ color: "var(--text)" }}>{MOCK_PARTNERS.length}</strong></span>
          <span>Client allocations: <strong style={{ color: "var(--text)" }}>{totalAllocations}</strong></span>
          <span>API keys: <strong style={{ color: "var(--text)" }}>{totalApiKeys}</strong></span>
          <span>Webhooks: <strong style={{ color: "var(--text)" }}>{MOCK_PARTNERS.filter((p) => p.webhook).length}</strong></span>
        </div>
      </div>

      <Card title="PARTNER MANAGEMENT">
        <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
          <Button 
            tone="accent" 
            size="sm" 
            onClick={() => setShowNewPartnerForm(!showNewPartnerForm)}
          >
            + Register Partner
          </Button>
        </div>

        {showNewPartnerForm && (
          <div style={{ 
            padding: 12, 
            background: "var(--bg2)", 
            borderRadius: 6, 
            marginBottom: 16,
            border: "1px solid var(--border)"
          }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <input 
                type="text" 
                placeholder="Partner Name" 
                style={{ 
                  padding: "8px 10px", 
                  borderRadius: 4, 
                  border: "1px solid var(--border)",
                  background: "var(--bg)",
                  color: "var(--text)",
                  fontSize: 13
                }} 
              />
              <input 
                type="text" 
                placeholder="Industry" 
                style={{ 
                  padding: "8px 10px", 
                  borderRadius: 4, 
                  border: "1px solid var(--border)",
                  background: "var(--bg)",
                  color: "var(--text)",
                  fontSize: 13
                }} 
              />
              <input 
                type="email" 
                placeholder="Contact Email" 
                style={{ 
                  padding: "8px 10px", 
                  borderRadius: 4, 
                  border: "1px solid var(--border)",
                  background: "var(--bg)",
                  color: "var(--text)",
                  fontSize: 13
                }} 
              />
              <div style={{ display: "flex", gap: 8 }}>
                <Button size="sm" tone="accent" onClick={() => setShowNewPartnerForm(false)}>Create</Button>
                <Button size="sm" tone="default" onClick={() => setShowNewPartnerForm(false)}>Cancel</Button>
              </div>
            </div>
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          {MOCK_PARTNERS.map((partner) => (
            <Collapsible
              key={partner.id}
              open={expandedPartner === partner.id}
              title={
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%", marginRight: 20 }}>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{partner.name}</div>
                  </div>
                  <div style={{ display: "flex", gap: 8, fontSize: 11, color: "var(--muted)" }}>
                    <span>{partner.industry}</span>
                    <Badge tone={partner.status === "active" ? "success" : "warning"}>
                      {partner.status}
                    </Badge>
                  </div>
                </div>
              }
              style={{ borderLeft: "2px solid var(--border)", paddingLeft: 12 }}
            >
              <div 
                onClick={() => setExpandedPartner(expandedPartner === partner.id ? null : partner.id)}
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(4, 1fr)",
                  gap: 16,
                  paddingBottom: 12,
                  paddingTop: 8,
                }}
              >
                <div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 6 }}>PARTNER ID</div>
                  <code style={{ 
                    fontFamily: "var(--mono)", 
                    fontSize: 11, 
                    background: "var(--bg2)", 
                    padding: "4px 6px",
                    borderRadius: 3,
                    display: "block",
                    wordBreak: "break-all",
                    color: "var(--accent)"
                  }}>
                    {partner.id}
                  </code>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 6 }}>API KEYS</div>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{partner.apiKeysCount}</div>
                  <Button size="sm" tone="default" style={{ marginTop: 6 }} onClick={() => alert("Manage API keys")}>
                    Manage
                  </Button>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 6 }}>ALLOCATIONS</div>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{partner.allocationsCount}</div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 6 }}>clients assigned</div>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 6 }}>STATUS</div>
                  <div style={{ 
                    fontSize: 11,
                    padding: "4px 8px",
                    borderRadius: 3,
                    background: partner.webhook ? "var(--accent)" : "var(--border)",
                    color: partner.webhook ? "white" : "var(--text)",
                  }}>
                    {partner.webhook ? "Webhooks ON" : "Webhooks OFF"}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 6 }}>Last: {partner.lastActivity}</div>
                </div>
              </div>
            </Collapsible>
          ))}
        </div>
        <Collapsible title="RECENT ACTIVITY" open={false} style={{ marginTop: 10, borderTop: "1px solid var(--border)" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
            {MOCK_AUDIT_LOG.map((log, idx) => (
              <div key={idx} style={{ 
                display: "grid",
                gridTemplateColumns: "140px 110px 1fr",
                gap: 12, 
                padding: "10px 0", 
                borderBottom: idx < MOCK_AUDIT_LOG.length - 1 ? "1px solid var(--border)" : "none",
                fontSize: 12,
                alignItems: "center"
              }}>
                <div style={{ 
                  color: "var(--muted)", 
                  fontFamily: "var(--mono)",
                  fontSize: 11
                }}>
                  {log.timestamp}
                </div>
                <div style={{ 
                  fontFamily: "var(--mono)",
                  background: "var(--bg2)",
                  padding: "3px 6px",
                  borderRadius: 3,
                  fontSize: 10,
                  color: "var(--accent)"
                }}>
                  {log.action}
                </div>
                <div>
                  <strong>{log.partner}</strong> — {log.details}
                </div>
              </div>
            ))}
          </div>
        </Collapsible>
      </Card>
    </div>
  );
}
