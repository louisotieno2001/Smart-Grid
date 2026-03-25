import React from "react";

type EmptyStateProps = {
  title: string;
  description?: string;
  action?: { label: string; onClick: () => void };
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div style={{ textAlign: "center", border: "1px dashed #c9c9c9", background: "#fff", borderRadius: 8, padding: 24 }}>
      <h3 style={{ margin: "0 0 8px" }}>{title}</h3>
      {description ? <p style={{ margin: "0 0 10px", color: "#666" }}>{description}</p> : null}
      {action ? <button onClick={action.onClick}>{action.label}</button> : null}
    </div>
  );
}
