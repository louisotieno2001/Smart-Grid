import { useMemo, useState } from "react";
import { Button } from "../../components/ui/Button";
import { createDemoRequest, createPricingInquiry, getApiBase } from "../../lib/api";

const PUBLIC_NAV = [
  { id: "landing", label: "Platform" },
  { id: "features", label: "Features" },
  { id: "changelog", label: "Changelog" },
  { id: "contact", label: "Contact" },
  { id: "forge", label: "Forge" },
  { id: "login", label: "Login" },
  { id: "signup", label: "Signup" },
];

function Landing({ goTo }) {
  return (
    <section className="public-surface public-hero">
      <div className="public-kicker">Industrial Energy Intelligence</div>
      <h1 className="public-title">EnergyAllocation helps multi-site operators reduce energy waste with clear, auditable actions.</h1>
      <p className="public-subtitle">
        Structured onboarding, validated data intake, ranked recommendations, and operational monitoring in one workflow.
      </p>
      <div className="public-hero-actions">
        <Button tone="accent" onClick={() => goTo("contact")}>Talk to sales</Button>
        <Button onClick={() => window.open(`${getApiBase()}/docs`, "_blank", "noopener,noreferrer")}>API docs</Button>
      </div>
    </section>
  );
}

function Features() {
  return (
    <section className="public-surface">
      <h2 className="public-section-title">Features</h2>
      <div className="public-stack">
        <div>
          <div className="public-feature-title">Portfolio visibility</div>
          <p className="public-copy">Track site performance, savings realization, and recommendation adoption across facilities.</p>
        </div>
        <div>
          <div className="public-feature-title">Actionable recommendations</div>
          <p className="public-copy">Prioritized opportunities with confidence, payback, and implementation readiness.</p>
        </div>
        <div>
          <div className="public-feature-title">Operational monitoring</div>
          <p className="public-copy">Alerts, drift signals, and retraining triggers for model quality and reliability.</p>
        </div>
      </div>
    </section>
  );
}

function Changelog() {
  return (
    <section className="public-surface">
      <h2 className="public-section-title">Changelog</h2>
      <div className="public-stack">
        <div>
          <div className="public-feature-title">v1.3 · Partner Integrations</div>
          <p className="public-copy">Added partner API keys, scopes, client allocations, and webhook support.</p>
        </div>
        <div>
          <div className="public-feature-title">v1.2 · Monitoring</div>
          <p className="public-copy">Added drift events, retraining jobs, and incident actions in alerts workflows.</p>
        </div>
        <div>
          <div className="public-feature-title">v1.1 · Intake Workflow</div>
          <p className="public-copy">Introduced connector validation, backfill jobs, and mapping readiness checks.</p>
        </div>
      </div>
    </section>
  );
}

function Forge() {
  const [status, setStatus] = useState("");

  async function onTalkToSales(plan) {
    try {
      const result = await createPricingInquiry({
        company: "Prospective Customer",
        contact_name: "Sales Contact",
        email: "contact@example.com",
        requested_plan: plan,
      });
      setStatus(`Inquiry submitted: ${result.inquiry_id}`);
    } catch {
      setStatus("Unable to submit pricing inquiry.");
    }
  }

  return (
    <section className="public-surface">
      <h2 className="public-section-title">Forge</h2>
      <p className="public-copy" style={{ marginBottom: 14 }}>
        Build and test integration-ready solutions with support for APIs, event hooks, and rollout planning.
      </p>
      <div className="public-stack">
        {[
          {
            plan: "Pilot",
            price: "€4,900 / month",
            desc: "1 facility, up to 50 appliances, monthly model refresh, standard support.",
            value: "pilot",
          },
          {
            plan: "Multi-Site",
            price: "€14,500 / month",
            desc: "Up to 6 facilities, API/webhooks, drift monitoring, role workflows, QBR reviews.",
            value: "multi-site",
          },
          {
            plan: "Performance Partnership",
            price: "Talk to sales",
            desc: "Enterprise scope, custom modeling and savings verification.",
            value: "performance",
          },
        ].map((tier) => (
          <div key={tier.plan} style={{ borderTop: "1px solid var(--border)", paddingTop: 12 }}>
            <div className="public-feature-title">{tier.plan}</div>
            <p className="public-price">{tier.price}</p>
            <p className="public-copy">{tier.desc}</p>
            <div style={{ marginTop: 8 }}><Button size="sm" onClick={() => onTalkToSales(tier.value)}>Talk to sales</Button></div>
          </div>
        ))}
      </div>
      {status ? <p className="public-status">{status}</p> : null}
    </section>
  );
}

function Contact() {
  return (
    <section className="public-surface">
      <h2 className="public-section-title">Contact</h2>
      <div className="public-stack">
        <p className="public-copy">Email: integration-support@energyallocation.com</p>
        <p className="public-copy">Sales: sales@energyallocation.com</p>
        <p className="public-copy">Support hours: Mon-Fri, 08:00-18:00 CET</p>
      </div>
    </section>
  );
}

function About() {
  return (
    <section className="public-surface">
      <h2 className="public-section-title">Platform</h2>
      <p className="public-copy">
        EnergyAllocation is built for industrial teams that need deployment-ready optimization guidance, measurable savings, and transparent operations.
      </p>
    </section>
  );
}

function AuthPage({ mode }) {
  const [status, setStatus] = useState("");

  function onSubmit(event) {
    event.preventDefault();
    setStatus(mode === "login" ? "Sign in submitted." : "Signup request submitted.");
  }

  return (
    <section className="public-surface public-auth-surface">
      <h2 className="public-section-title">{mode === "login" ? "Login" : "Create account"}</h2>
      <form onSubmit={onSubmit}>
        <div className="form-group">
          <label className="form-label">Work email</label>
          <input className="form-input" placeholder="name@company.com" />
        </div>
        <div className="form-group">
          <label className="form-label">Password</label>
          <input type="password" className="form-input" placeholder="••••••••" />
        </div>
        <Button tone="accent" type="submit">{mode === "login" ? "Sign in" : "Create account"}</Button>
      </form>
      {status ? <p className="public-status">{status}</p> : null}
    </section>
  );
}

function DemoRequest() {
  const [status, setStatus] = useState("");

  async function onSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const payload = {
      company: String(form.get("company") || ""),
      contact_name: String(form.get("contact_name") || ""),
      email: String(form.get("email") || ""),
      facilities_count: Number(form.get("facilities_count") || 0),
      annual_energy_spend_eur: Number(form.get("annual_energy_spend_eur") || 0),
      message: String(form.get("message") || ""),
    };

    try {
      const result = await createDemoRequest(payload);
      setStatus(`Request submitted: ${result.request_id}`);
      event.currentTarget.reset();
    } catch {
      setStatus("Unable to submit request right now.");
    }
  }

  return (
    <section className="public-surface public-auth-surface">
      <h2 className="public-section-title">Request a demo</h2>
      <form onSubmit={onSubmit}>
        <div className="form-group">
          <label className="form-label">Company</label>
          <input name="company" className="form-input" required />
        </div>
        <div className="form-group">
          <label className="form-label">Contact name</label>
          <input name="contact_name" className="form-input" required />
        </div>
        <div className="form-group">
          <label className="form-label">Email</label>
          <input name="email" type="email" className="form-input" required />
        </div>
        <div className="form-group">
          <label className="form-label">Facilities count</label>
          <input name="facilities_count" type="number" className="form-input" />
        </div>
        <div className="form-group">
          <label className="form-label">Annual energy spend (EUR)</label>
          <input name="annual_energy_spend_eur" type="number" className="form-input" />
        </div>
        <div className="form-group">
          <label className="form-label">Notes</label>
          <input name="message" className="form-input" />
        </div>
        <Button tone="accent" type="submit">Submit</Button>
      </form>
      {status ? <p className="public-status">{status}</p> : null}
    </section>
  );
}

export function PublicSite({ enterApp }) {
  const [page, setPage] = useState("landing");

  const content = useMemo(() => {
    if (page === "features") return <Features />;
    if (page === "changelog") return <Changelog />;
    if (page === "contact") return <Contact />;
    if (page === "forge") return <Forge />;
    if (page === "about") return <About />;
    if (page === "login") return <AuthPage mode="login" />;
    if (page === "signup") return <AuthPage mode="signup" />;
    if (page === "demo") return <DemoRequest />;
    return <Landing goTo={setPage} />;
  }, [page]);

  return (
    <div className="public-root">
      <header className="public-header">
        <div className="logo-text">EnergyAllocation</div>
        <nav className="public-nav">
          {PUBLIC_NAV.map((item) => (
            <button key={item.id} className={`public-nav-item ${page === item.id ? "active" : ""}`} onClick={() => setPage(item.id)}>
              {item.label}
            </button>
          ))}
        </nav>
        <Button tone="accent" onClick={enterApp}>Open app</Button>
      </header>
      <main className="public-main">{content}</main>
    </div>
  );
}
