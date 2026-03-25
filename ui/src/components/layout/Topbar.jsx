import { Button } from "../ui/Button";
import { Icon } from "../../lib/icons";

export function Topbar({ title, breadcrumb, onRefresh, onSettings }) {
  return (
    <div className="topbar">
      <div className="topbar-left">
        <div>
          <div className="page-title">{title}</div>
          <div className="breadcrumb">{breadcrumb}</div>
        </div>
      </div>
      <div className="topbar-right">
        <Button tone="ghost" onClick={onRefresh}><Icon name="refresh" size={13} /> Refresh</Button>
        <Button tone="ghost" onClick={onSettings}><Icon name="settings" size={13} /> Settings</Button>
      </div>
    </div>
  );
}
