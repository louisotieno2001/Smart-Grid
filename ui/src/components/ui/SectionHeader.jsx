export function SectionHeader({ title, action }) {
  return (
    <div className="section-hdr">
      <div className="section-title">{title}</div>
      {action}
    </div>
  );
}
