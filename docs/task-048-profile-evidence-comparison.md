# Task 048: OMS profile evidence comparison

This tooling-only feature compares explicitly linked source candidates with exact, fixed OMS 2.5 profile facts. It preserves source provenance and OMS normative traceability and reports observed/decision alignment without selecting evidence or changing authoring state.

The RF FM Demod example links only ServiceStatus selector, direction, and timing kind. Its topic (`mission.service-status`) and rate (`1.0 Hz`) remain author-owned evidence because OMS fixes neither. PositionReport and SignalReport candidates remain unlinked; no function ownership is inferred.

The flow is source evidence → profile-evidence comparison → authoring workflow → materialized contract → `OP_*` validation. Only the final validation establishes profile conformance.
