export function mapFacilityToUi(item, index = 0) {
  const defaultSavings = [284, 241, 198, 312, 187, 198][index % 6];
  const defaultSpend = [3200, 2900, 1800, 1400, 980, 760][index % 6];

  const saving = Number(item.saving ?? defaultSavings);
  const spend = Number(item.spend ?? defaultSpend);
  const realized = Number(item.realized ?? Math.max(10, Math.round(saving * 0.35)));

  return {
    id: item.id || `fac_ui_${index}`,
    name: item.name || `Facility ${index + 1}`,
    city: item.city || "Unknown",
    country: item.country || "N/A",
    status: item.status || "active",
    spend,
    saving,
    realized,
    intensity: Number(item.intensity ?? 380),
    mape: Number(item.mape ?? 4.5),
    recs: Number(item.recs ?? 1),
    drift: item.drift || "stable",
    appliances: Number(item.appliances ?? 20),
  };
}

export function mapRecommendationToUi(item, index = 0) {
  const saving = Number(item.projected_annual_savings_eur ?? 25000) / 1000;
  return {
    id: item.recommendation_id || `rec_ui_${index}`,
    appliance: item.appliance_id || "appliance",
    title: item.title || "Optimization recommendation",
    saving: Number(saving.toFixed(1)),
    confidence: Number(item.confidence ?? 0.75),
    effort: item.effort || "medium",
    payback_months: Number(item.payback_months ?? 6),
    readiness: Number(item.implementation_readiness ?? 0.7),
    status: item.status || "active",
    category: item.category || "Operational",
    body: item.detail || "Generated from facility model run and tariff-aware ranking logic.",
  };
}

export function mapAlertToUi(item, index = 0) {
  return {
    id: item.alert_id || `alt_ui_${index}`,
    severity: item.severity || "warning",
    state: item.state || "open",
    source_type: item.source_type || "system",
    title: item.title || `${item.source_type || "system"} alert`,
    detail: item.detail || item.routing_policy || "Operational alert triggered.",
    facility: item.facility_id || "facility",
    sla_minutes: Number(item.sla_minutes ?? 60),
    ago: item.ago || "just now",
  };
}

export function mapDriftToUi(item, index = 0) {
  return {
    name: item.monitored_segment || item.feature_distribution_change || `feature_${index + 1}`,
    psi: Number(item.threshold_breached ?? item.psi ?? 0.1),
    status: item.retraining_action || item.status || "monitoring",
  };
}
