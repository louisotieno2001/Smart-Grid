import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell({ navItems, page, setPage, title, breadcrumb, onRefresh, onSettings, children }) {
  return (
    <div className="app">
      <Sidebar navItems={navItems} page={page} setPage={setPage} />
      <div className="main">
        <Topbar title={title} breadcrumb={breadcrumb} onRefresh={onRefresh} onSettings={onSettings} />
        {children}
      </div>
    </div>
  );
}
