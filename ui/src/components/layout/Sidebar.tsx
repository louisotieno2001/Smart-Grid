import React from "react";
import { NavLink, useLocation } from "react-router-dom";

export function Sidebar() {
  const { pathname } = useLocation();
  const match = pathname.match(/^\/sites\/([^/]+)/);
  const siteId = match?.[1] || null;

  const links = siteId
    ? [
        { to: "/sites", label: "Sites" },
        { to: `/sites/${siteId}`, label: "Dashboard" },
        { to: `/sites/${siteId}/devices`, label: "Devices" },
        { to: `/sites/${siteId}/telemetry`, label: "Telemetry" },
        { to: `/sites/${siteId}/optimization`, label: "Optimization" },
        { to: `/sites/${siteId}/commands`, label: "Commands" },
        { to: `/sites/${siteId}/savings`, label: "Savings" },
        { to: `/sites/${siteId}/simulation`, label: "Simulation" }
      ]
    : [{ to: "/sites", label: "Sites" }];

  return (
    <aside style={{ width: 230, borderRight: "1px solid #ddd", padding: 12 }}>
      {links.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          style={({ isActive }) => ({
            display: "block",
            padding: "8px 10px",
            marginBottom: 6,
            textDecoration: "none",
            color: isActive ? "#0d47a1" : "#222",
            background: isActive ? "#e8f0fe" : "transparent",
            borderRadius: 6
          })}
        >
          {item.label}
        </NavLink>
      ))}
    </aside>
  );
}
