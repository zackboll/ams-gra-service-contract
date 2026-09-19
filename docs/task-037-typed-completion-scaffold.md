# Task 037 — Typed completion mapping and profile-derived authoring scaffold

Task 037 adds tooling-only `completion-mapping.schema.json` and
`completion_scaffold.py`. Bounded destinations cover service/standards fields,
context assertions, profile-required function fields, and profile-required
exchange fields. Validation rejects duplicate/unknown targets or destinations,
unknown profile lookup, profile-owned overrides, timing/kind incompatibility,
wrong values, and context disagreement.

The IR Search and Track example maps Service Status topic/rate but intentionally
leaves PositionReport and ObservationMeasurementReport decisions unmapped. The
scaffold reports structural missing fields from profile shape without constructing
a contract. Specific-function authoring, Capability completion, materialization,
apply/write, SC validation, and satisfaction analysis remain pending.
