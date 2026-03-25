import { useMemo, useState } from "react";
import { AppShell } from "../components/layout/AppShell";
import { NAV } from "../lib/constants";
import { PAGE_COMPONENTS } from "./routes";
import { PublicSite } from "../features/public/PublicSite";
import { getApiBase } from "../lib/api";

export default function App() {
  const [surface, setSurface] = useState("public");
  const [page, setPage] = useState("portfolio");
  const current = PAGE_COMPONENTS[page];
  const Page = current.component;

  const navItems = useMemo(() => {
    let lastSection = "";
    return NAV.map((item) => {
      const showSection = item.section !== lastSection;
      lastSection = item.section;
      return { ...item, showSection };
    });
  }, []);

  if (surface === "public") {
    return <PublicSite enterApp={() => setSurface("app")} />;
  }

  function handleRefresh() {
    window.location.reload();
  }

  function handleSettings() {
    window.open(`${getApiBase()}/docs`, "_blank", "noopener,noreferrer");
  }

  return (
    <AppShell
      navItems={navItems}
      page={page}
      setPage={setPage}
      title={current.title}
      breadcrumb={current.breadcrumb}
      onRefresh={handleRefresh}
      onSettings={handleSettings}
    >
      <Page />
    </AppShell>
  );
}
