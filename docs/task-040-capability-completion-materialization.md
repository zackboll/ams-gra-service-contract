# Task 040 — Explicit Capability completion and materialization

Task 040 adds explicit portable Capability authoring to the completion pipeline.
The `completion-capabilities` artifact is intentionally structural; author
decisions mapped through typed destinations supply every portable Capability ID,
name, and position-dependency Boolean. Materialization remains fail-closed and
validates the constructed contract with `SC_*` then `OP_*` before emitting JSON.

The OMS 2.5 profile remains the sole source for Section 3.3 role metadata and
applicability. Capability functions have no generated exchanges. The synthetic
two-Capability service exercise demonstrates ESM (position required), Radar
(position not required), six per-Capability functions, and one unowned Position
Information Processing function.
