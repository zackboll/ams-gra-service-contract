# Completion Capabilities

`--capabilities` accepts a tooling-only `completion-capabilities` v0.1 artifact.
Its bounded `key` is structural only: it is never a portable Capability ID or
display name.

- no artifact means Capability facts are unknown: `capabilities` is omitted and
  no Section 3.3 functions are created;
- an artifact with `capabilities: []` affirmatively declares zero Capabilities;
- a non-empty artifact declares topology in author declaration order.

Portable `id`, `name`, and `requires_position_information` values require typed
`capability_field` mappings and explicit decisions. The position field must be a
real Boolean. Capability-related function ID/name/optional description decisions
use `capability_function_field` or `component_capability_function_field`.

Section 3.3 topology comes only from the validated OMS profile plus explicit
Capability facts. It is never inferred from names, messages, RF/IR/ESM/MFA
terminology, or specific-function structure. Per-Capability profile roles are
created in declared Capability order then profile order. A component-level
Position Information Processing role appears once only when any explicit
Capability resolves `requires_position_information: true`; it has no Capability
owner. Isolators retain portable Capability facts but receive no OMS 2.5 Section
3.3 functions.
