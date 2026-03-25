import React from "react";
import { useParams } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";

export function DevicesPage() {
  const { siteId } = useParams();
  return (
    <div style={{ display: "grid", gap: 12 }}>
      <PageHeader title="Devices" subtitle={siteId} />
      <Card title="DEFERRED">
        <div style={{ color: "#ef6c00", display: "grid", gap: 4 }}>
          <div>DEFERRED: `POST /api/v1/sites/{`{site_id}`}/assets` is not implemented.</div>
          <div>DEFERRED: `POST /api/v1/assets/{`{asset_id}`}/devices` is not implemented.</div>
          <div>DEFERRED: `GET /api/v1/sites/{`{site_id}`}/devices` is not implemented.</div>
          <div>DEFERRED: `POST /api/v1/devices/{`{device_id}`}/mappings` is not implemented.</div>
        </div>
      </Card>
    </div>
  );
}
