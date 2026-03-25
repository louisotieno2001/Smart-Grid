import React from "react";
import { useAuth } from "../../features/auth/useAuth";

export function Topbar() {
  const { user, logout } = useAuth();
  return (
    <header style={{ height: 56, borderBottom: "1px solid #ddd", display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 16px" }}>
      <strong>EMS Operational Console</strong>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span style={{ color: "#555" }}>{user?.email || "Unknown user"}</span>
        <button onClick={logout}>Logout</button>
      </div>
    </header>
  );
}
