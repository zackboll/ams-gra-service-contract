# Task 036 — Completion author decisions

Task 036 adds a non-normative, separate author-decision overlay to the Task 035
completion worksheet. Its deliberately separate stages are:

1. an **evidence candidate**, an observed possible value with source provenance;
2. an **author decision**, explicit author intent for an opaque worksheet target;
3. an **authored contract semantic**, a value written into and validated as part
   of a portable Service Contract.

Only the first two stages are implemented. `completion-decisions.schema.json`
permits a decision to select exactly one named candidate or supply one scalar
author value. Selected candidates preserve their individual provenance;
author-supplied values intentionally have no source record. Decisions neither
alter evidence nor claim OMS profile satisfaction.

The worksheet retains every candidate, including same-value candidates from
different sources and all conflicting evidence. A recorded decision removes that
target from remaining open conflict decisions while leaving its conflict history
visible. Services and Subsystems still show the Capability inventory prompt;
Isolators do not.

There is no candidate-to-contract field mapping, contract scaffold, JSON Patch,
JSONPath execution, contract generation, contract editing, or apply operation.
Nothing becomes a Service Contract field merely because it was observed or
selected in this tooling workspace. A future typed apply step must construct a
portable contract and pass ordinary `SC_*` validation.
