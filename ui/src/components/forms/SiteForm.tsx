import React, { useState } from "react";
import type { SiteCreateBody } from "../../types";

type Props = {
  onSubmit: (body: SiteCreateBody) => void;
  loading?: boolean;
};

export function SiteForm({ onSubmit, loading }: Props) {
  const [name, setName] = useState("");
  const [timezone, setTimezone] = useState("UTC");

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          site_id: `site_${Date.now()}`,
          name,
          timezone,
          reserve_soc_min: 20,
          polling_interval_seconds: 300
        });
      }}
      style={{ display: "grid", gap: 8 }}
    >
      <input required placeholder="Site name" value={name} onChange={(e) => setName(e.target.value)} />
      <input required placeholder="Timezone" value={timezone} onChange={(e) => setTimezone(e.target.value)} />
      <button disabled={loading} type="submit">
        {loading ? "Creating..." : "Create site"}
      </button>
    </form>
  );
}
