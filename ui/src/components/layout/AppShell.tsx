import React from "react";
import { Outlet } from "react-router-dom";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell() {
  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <Topbar />
      <div style={{ display: "flex", minHeight: 0, flex: 1 }}>
        <Sidebar />
        <main style={{ flex: 1, overflow: "auto", padding: 16, background: "#fafafa" }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
