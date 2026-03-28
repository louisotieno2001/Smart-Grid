# Smart-Grid Reality Sync TODO (March 2026)

## Completed
- [x] Consolidated backend on `/api/v1` and retired legacy runtime paths.
- [x] Landed core edge modules (`modbus_adapter`, `decoder`, `poller`, `staleness`, `replay`, `runtime`, `sqlite` storage).
- [x] Added edge-focused tests in `tests/edge/` and validated current passing test suite.
- [x] Added API support for edge gateway and point mapping management.

## True blockers (remaining)
- [ ] Production edge runner lifecycle is not fully operationalized (no documented always-on supervised runtime deployment path).
- [ ] Messaging transport hardening is incomplete for production (final MQTT path and/or resilient HTTP fallback policy).
- [ ] End-to-end command reconciliation validation across API intent -> edge apply -> ack/fail needs full integration coverage.
- [ ] Field runbook/soak-test evidence for outages, reconnects, and replay behavior is still pending.

## Next actions
- [ ] Create and document a dedicated edge runtime startup command/profile.
- [ ] Finalize transport strategy and configuration toggles (`mqtt|http`) with failure-mode behavior.
- [ ] Add integration scenarios for connectivity loss/recovery and duplicate command delivery.
- [ ] Publish deployment and on-call troubleshooting runbook for edge operations.

