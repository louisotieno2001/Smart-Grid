# Pricing and ROI Calculator Design

## Pricing Architecture
- Platform fee: per client account
- Facility fee: per active site
- Data scale fee: appliance/channel/data volume bands
- Optional value-based component: verified realized savings share

## Commercial Tiers
### Tier A — Growth industrial
- Base platform + 1 facility + up to 50 appliances
- Standard dashboards, monthly retraining, email support

### Tier B — Enterprise operations
- Multi-site, connectors, advanced recommendations, drift monitoring
- Role-based workflows, API/webhooks, quarterly reviews

### Tier C — Performance partnership
- Enterprise plus custom modeling and multi-site benchmarking
- Savings verification support and optional success fee

## ROI Inputs
- annual energy spend
- facilities count
- appliance count
- average tariff
- production profile
- expected data availability
- optimization maturity
- implementation capacity
- target payback threshold

## Core Logic
Let:
- projected savings = annual spend × benchmark inefficiency × data readiness × maturity factor × profile factor
- realized savings = projected savings × implementation adoption × realization confidence × capacity factor
- net annual value = realized savings − platform cost − implementation cost
- payback months = first-year cost / (realized savings / 12)
- ROI% = (net annual value / first-year cost) × 100

Sensitivity outputs:
- conservative
- expected
- aggressive

## Sales Calculator Modes
1. Fast estimate: 5-6 inputs for discovery calls
2. Solution design: adds appliance mix and data readiness
3. Contract-grade: final commercial case with assumptions and sensitivity range

## Recommendation
Use fixed subscription for software baseline, optional implementation services, and optional success fee above verified baseline.
