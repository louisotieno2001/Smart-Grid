import React from "react";
import { Navigate, createBrowserRouter } from "react-router-dom";
import { AppShell } from "../components/layout/AppShell";
import { RequireAuth } from "../features/auth/useAuth";
import { LoginPage } from "../features/auth/LoginPage";
import { SitesPage } from "../features/sites/SitesPage";
import { SiteDetailPage } from "../features/sites/SiteDetailPage";
import { DevicesPage } from "../features/devices/DevicesPage";
import { TelemetryPage } from "../features/telemetry/TelemetryPage";
import { OptimizationPage } from "../features/optimization/OptimizationPage";
import { CommandsPage } from "../features/commands/CommandsPage";
import { SavingsPage } from "../features/savings/SavingsPage";
import { SimulationPage } from "../features/simulation/SimulationPage";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  {
    path: "/",
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <Navigate to="/sites" replace /> },
      { path: "sites", element: <SitesPage /> },
      { path: "sites/:siteId", element: <SiteDetailPage /> },
      { path: "sites/:siteId/devices", element: <DevicesPage /> },
      { path: "sites/:siteId/telemetry", element: <TelemetryPage /> },
      { path: "sites/:siteId/optimization", element: <OptimizationPage /> },
      { path: "sites/:siteId/commands", element: <CommandsPage /> },
      { path: "sites/:siteId/savings", element: <SavingsPage /> },
      { path: "sites/:siteId/simulation", element: <SimulationPage /> }
    ]
  }
]);
