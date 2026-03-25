export function Button({ tone = "default", size = "md", className = "", ...props }) {
  const toneClass = tone === "accent" ? "btn-accent" : tone === "ghost" ? "btn-ghost" : tone === "danger" ? "btn-danger" : "";
  const sizeClass = size === "sm" ? "btn-sm" : "";
  return <button className={`btn ${toneClass} ${sizeClass} ${className}`.trim()} {...props} />;
}
