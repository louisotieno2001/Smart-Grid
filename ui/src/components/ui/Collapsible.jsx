import { useEffect, useState } from "react";

export function Collapsible({ title, open = false, children, style = {} }) {
  const [isOpen, setIsOpen] = useState(open);

  useEffect(() => {
    setIsOpen(open);
  }, [open]);

  return (
    <div style={style}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        style={{
          padding: "12px 0",
          borderBottom: "1px solid var(--border)",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          userSelect: "none",
          transition: "opacity 0.2s",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.8")}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
      >
        <div style={{ fontWeight: 500, fontSize: 13, width: "100%" }}>{title}</div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 20,
            height: 20,
            transition: "transform 0.2s",
            transform: isOpen ? "rotate(90deg)" : "rotate(0deg)",
            color: "var(--muted)",
          }}
        >
          ▶
        </div>
      </div>
      {isOpen && <div style={{ paddingTop: 12 }}>{children}</div>}
    </div>
  );
}
