import React from "react";

type CardProps = {
  title?: string;
  children: React.ReactNode;
};

export function Card({ title, children }: CardProps) {
  return (
    <section style={{ background: "#fff", border: "1px solid #e0e0e0", borderRadius: 8, padding: 14 }}>
      {title ? <h3 style={{ marginTop: 0, marginBottom: 10, fontSize: 15 }}>{title}</h3> : null}
      {children}
    </section>
  );
}
