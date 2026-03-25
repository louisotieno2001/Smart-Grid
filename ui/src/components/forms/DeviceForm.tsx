import React, { useState } from "react";
import type { DeviceCreateBody } from "../../types";

type Props = {
  onSubmit: (body: DeviceCreateBody) => void;
  loading?: boolean;
};

export function DeviceForm({ onSubmit, loading }: Props) {
  const [deviceType, setDeviceType] = useState("battery_inverter");
  const [protocol, setProtocol] = useState("modbus_tcp");
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit({ device_type: deviceType, protocol, metadata: {} });
      }}
      style={{ display: "grid", gap: 8 }}
    >
      <input value={deviceType} onChange={(e) => setDeviceType(e.target.value)} placeholder="device_type" />
      <input value={protocol} onChange={(e) => setProtocol(e.target.value)} placeholder="protocol" />
      <button disabled={loading} type="submit">
        {loading ? "Adding..." : "Add device"}
      </button>
    </form>
  );
}
