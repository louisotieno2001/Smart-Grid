import React from "react";

type PageHeaderProps = {
  title: string;
  subtitle?: string;
  right?: React.ReactNode;
};

export function PageHeader({ title, subtitle, right }: PageHeaderProps) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
      <div>
        <h1 style={{ margin: 0, fontSize: 22 }}>{title}</h1>
        {subtitle ? <p style={{ margin: "4px 0 0", color: "#555" }}>{subtitle}</p> : null}
      </div>
      {right}
    </div>
  );
}
