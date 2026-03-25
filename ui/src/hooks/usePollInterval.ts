export function usePollInterval(type: "telemetry" | "optimization" | "commands" | "simulationRunning" | "default") {
  switch (type) {
    case "telemetry":
      return 30_000;
    case "optimization":
      return 60_000;
    case "commands":
      return 30_000;
    case "simulationRunning":
      return 5_000;
    default:
      return false;
  }
}
