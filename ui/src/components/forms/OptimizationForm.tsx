import React, { useState } from "react";
import type { OptimizationRunBody } from "../../types";

type Props = {
  onSubmit: (body: OptimizationRunBody) => void;
  loading?: boolean;
};

export function OptimizationForm({ onSubmit, loading }: Props) {
  const [mode, setMode] = useState<"live" | "simulation" | "backtest">("live");
  const [horizon, setHorizon] = useState(60);
  const [step, setStep] = useState(5);
  const [allowExport, setAllowExport] = useState(true);
  const [reserveSocMin, setReserveSocMin] = useState(20);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({
          mode,
          horizon_minutes: horizon,
          step_minutes: step,
          allow_export: allowExport,
          reserve_soc_min: reserveSocMin
        });
      }}
      style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(5,minmax(120px,1fr))" }}
    >
      <select value={mode} onChange={(e) => setMode(e.target.value as "live" | "simulation" | "backtest")}>
        <option value="live">live</option>
        <option value="simulation">simulation</option>
        <option value="backtest">backtest</option>
      </select>
      <input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} />
      <input type="number" value={step} onChange={(e) => setStep(Number(e.target.value))} />
      <label style={{ display: "flex", gap: 6, alignItems: "center" }}>
        <input type="checkbox" checked={allowExport} onChange={(e) => setAllowExport(e.target.checked)} />allow export
      </label>
      <input type="number" value={reserveSocMin} onChange={(e) => setReserveSocMin(Number(e.target.value))} />
      <button disabled={loading} type="submit" style={{ gridColumn: "span 5" }}>
        {loading ? "Running..." : "Run optimization"}
      </button>
    </form>
  );
}
