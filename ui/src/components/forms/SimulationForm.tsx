import React, { useState } from "react";
import type { SimulationRunBody } from "../../types";

type Props = {
  onSubmit: (body: SimulationRunBody) => void;
  loading?: boolean;
};

export function SimulationForm({ onSubmit, loading }: Props) {
  const [mode, setMode] = useState<"simulation" | "backtest">("simulation");
  const [stepMinutes, setStepMinutes] = useState(5);
  const [allowExport, setAllowExport] = useState(true);
  const [reserveSocMin, setReserveSocMin] = useState(20);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ mode, step_minutes: stepMinutes, allow_export: allowExport, reserve_soc_min: reserveSocMin });
      }}
      style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(4,minmax(120px,1fr))" }}
    >
      <select value={mode} onChange={(e) => setMode(e.target.value as "simulation" | "backtest")}>
        <option value="simulation">simulation</option>
        <option value="backtest">backtest</option>
      </select>
      <input type="number" value={stepMinutes} onChange={(e) => setStepMinutes(Number(e.target.value))} />
      <label style={{ display: "flex", gap: 6, alignItems: "center" }}>
        <input type="checkbox" checked={allowExport} onChange={(e) => setAllowExport(e.target.checked)} />allow export
      </label>
      <input type="number" value={reserveSocMin} onChange={(e) => setReserveSocMin(Number(e.target.value))} />
      <button disabled={loading} type="submit" style={{ gridColumn: "span 4" }}>
        {loading ? "Running..." : "Run simulation"}
      </button>
    </form>
  );
}
