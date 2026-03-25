export const FACILITIES = [
  { id:"fac_001", name:"Steelworks A", city:"Hamburg", country:"DE", status:"active", spend:3200, saving:284, realized:41, intensity:412, mape:3.8, recs:9, drift:"stable", appliances:78 },
  { id:"fac_002", name:"Steelworks B", city:"Duisburg", country:"DE", status:"active", spend:2900, saving:241, realized:38, intensity:438, mape:4.1, recs:7, drift:"stable", appliances:64 },
  { id:"fac_003", name:"Rolling Mill C", city:"Łódź", country:"PL", status:"active", spend:1800, saving:198, realized:22, intensity:381, mape:4.4, recs:6, drift:"minor", appliances:52 },
  { id:"fac_004", name:"Casting Plant D", city:"Lyon", country:"FR", status:"active", spend:1400, saving:312, realized:51, intensity:344, mape:3.5, recs:5, drift:"stable", appliances:41 },
  { id:"fac_005", name:"Forging E", city:"Bilbao", country:"ES", status:"active", spend:980, saving:187, realized:28, intensity:509, mape:4.9, recs:3, drift:"watch", appliances:38 },
  { id:"fac_006", name:"Tube Mill F", city:"Ostrava", country:"CZ", status:"new", spend:760, saving:198, realized:104, intensity:371, mape:3.2, recs:1, drift:"stable", appliances:29 },
];

export const RECOMMENDATIONS = [
  { id:"rec_001", appliance:"Arc furnace #1 & #2", title:"Load-shift to off-peak tariff window", saving:112, confidence:0.91, effort:"medium", payback_months:4.2, readiness:0.74, status:"active", category:"Load shifting", body:"Both furnaces run peak operations 09:00–17:00 coinciding with maximum tariff rates. Shift 4.2 h/day of tap-to-tap cycles to the 22:00–06:00 window without production impact." },
  { id:"rec_002", appliance:"Compressed air system", title:"Pressure set-point reduction 8.2 → 7.0 bar", saving:58, confidence:0.95, effort:"low", payback_months:1.8, readiness:0.91, status:"accepted", category:"Equipment tuning", body:"Sustained over-pressure detected in ring main. No processes require above 6.8 bar. 1.2 bar reduction cuts compressor load by ~14%. Highest effort-to-saving ratio on site." },
  { id:"rec_003", appliance:"Rolling mill motor bank", title:"Demand response enrolment — grid stress events", saving:39, confidence:0.78, effort:"high", payback_months:9.1, readiness:0.42, status:"active", category:"Demand response", body:"12 MW motor bank qualifies for grid balancing programmes. Estimated 15–22 events/year with 30-min response window. Requires load controller installation." },
  { id:"rec_004", appliance:"Ladle preheater A", title:"Eliminate standby idling between heats", saving:24, confidence:0.89, effort:"low", payback_months:2.1, readiness:0.88, status:"active", category:"Equipment tuning", body:"Preheater running full power during inter-heat gaps averaging 38 min. Stepped ramp-down to 30% during gaps >20 min. PLC parameter change only — no hardware required." },
  { id:"rec_005", appliance:"HVAC production floor", title:"Reduce ventilation during non-production hours", saving:17, confidence:0.92, effort:"low", payback_months:1.2, readiness:0.95, status:"implemented", category:"Scheduling", body:"HVAC runs at 100% ventilation 24/7. Model identifies 7h/day low-occupancy where 40% setback is safe per thermal mass analysis. BMS schedule update only." },
];

export const ALERTS = [
  { id:"alt_001", severity:"high", state:"open", source_type:"connector", title:"Connector offline — CH-08 (Rolling mill)", detail:"Modbus polling agent lost connection at 14:32 UTC. 47 min without data.", facility:"fac_003", sla_minutes:30, ago:"52m ago" },
  { id:"alt_002", severity:"warning", state:"acknowledged", source_type:"model", title:"Feature drift detected — tariff_zone_flag", detail:"PSI score 0.24 exceeds threshold 0.20. Scheduled retrain triggered.", facility:"fac_005", sla_minutes:240, ago:"2h ago" },
  { id:"alt_003", severity:"info", state:"open", source_type:"business", title:"Recommendation aging — rec_003 (Demand response)", detail:"Accepted recommendation has not been implemented in 28 days. Target date approaching.", facility:"fac_001", sla_minutes:1440, ago:"6h ago" },
  { id:"alt_004", severity:"critical", state:"investigating", source_type:"data_quality", title:"Data completeness below 90% — Forging E CH-22", detail:"98 consecutive null readings on induction heater channel. Possible sensor fault.", facility:"fac_005", sla_minutes:15, ago:"8m ago" },
];

export const DRIFT_FEATURES = [
  { name:"tariff_zone_flag", psi:0.24, status:"retrain_triggered" },
  { name:"rolling_mean_1h", psi:0.11, status:"stable" },
  { name:"lag_t168", psi:0.07, status:"stable" },
  { name:"peak_coincidence", psi:0.18, status:"monitoring" },
  { name:"cost_rate", psi:0.05, status:"stable" },
  { name:"throughput_ratio", psi:0.03, status:"stable" },
];

export const API_ENDPOINTS = [
  { method:"POST", path:"/v1/clients/{client_id}/facilities", desc:"Create facility in draft state", tag:"Onboarding" },
  { method:"POST", path:"/v1/facilities/{facility_id}/connectors", desc:"Attach metering connector to facility", tag:"Onboarding" },
  { method:"POST", path:"/v1/connectors/{connector_id}/validate", desc:"Validate connector health and detected channels", tag:"Onboarding" },
  { method:"GET", path:"/v1/connectors/{connector_id}/channels", desc:"List detected meter channels (cursor paginated)", tag:"Ingestion" },
  { method:"POST", path:"/v1/facilities/{facility_id}/appliances", desc:"Create appliance and map to channel IDs", tag:"Modeling" },
  { method:"POST", path:"/v1/facilities/{facility_id}/ingestion/imports", desc:"Submit historical CSV/parquet/jsonl import", tag:"Ingestion" },
  { method:"GET", path:"/v1/ingestion/imports/{import_id}", desc:"Poll import job progress", tag:"Ingestion" },
  { method:"POST", path:"/v1/facilities/{facility_id}/features/materialize", desc:"Trigger feature vector materialization for window", tag:"Modeling" },
  { method:"POST", path:"/v1/facilities/{facility_id}/models/runs", desc:"Start XGBoost + IsolationForest model run", tag:"Modeling" },
  { method:"GET", path:"/v1/models/runs/{model_run_id}", desc:"Get model run metrics, SHAP artifacts, validation", tag:"Modeling" },
  { method:"GET", path:"/v1/facilities/{facility_id}/recommendations", desc:"List ranked recommendations (status/sort/cursor)", tag:"Recommendations" },
  { method:"POST", path:"/v1/recommendations/{recommendation_id}/decision", desc:"Accept or reject a recommendation", tag:"Recommendations" },
  { method:"POST", path:"/v1/recommendations/{recommendation_id}/implementations", desc:"Record implementation milestone — starts savings window", tag:"Recommendations" },
  { method:"GET", path:"/v1/facilities/{facility_id}/savings", desc:"Savings summary: projected vs realized by appliance", tag:"Monitoring" },
  { method:"GET", path:"/v1/facilities/{facility_id}/alerts", desc:"List alerts — filter by severity/status", tag:"Monitoring" },
  { method:"GET", path:"/v1/facilities/{facility_id}/drift-events", desc:"List model drift events", tag:"Monitoring" },
  { method:"POST", path:"/v1/webhooks/subscriptions", desc:"Subscribe to platform events via webhook", tag:"Integrations" },
];

export const CONNECTORS = [
  { id: "sentron", name: "Siemens SENTRON", detail: "Live metering gateway · 148 channels", icon: "⚡", connected: true },
  { id: "modbus", name: "Modbus / SCADA", detail: "PLC historian bridge · 92 tags", icon: "⇆", connected: true },
  { id: "csv", name: "CSV / Parquet import", detail: "Manual backfill and scheduled batch drops", icon: "⬆", connected: false },
];
