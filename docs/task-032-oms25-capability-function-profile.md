# Task 032 — OMS 2.5 Capability function profile

## Source basis

This implementation uses the pinned official OMSC-INS-003 Rev M OMS 2.5 DOCX at
`open-arsenal/oms` revision `726272bd0390982a759c91a9cf4e13b81c2b510b`, as
classified in Tasks 026–031. It does not repeat their OOXML analysis.

## Portable and profile model

Capability presence comes only from the optional portable `capabilities` member.
Omission means facts are unknown and produces no Section 3.3 inventory result;
an explicit empty array affirmatively declares no Capabilities. Section 3.3
selectors apply only to Services and Subsystems, never Isolators.

`functions[].capability` is the sole ownership link for the three repeated roles.
Task 031 ownership cannot distinguish their function types, so Task 032 adds
optional bounded `functions[].standard_role`: `capability_status`,
`capability_enable_disable`, `capability_operations`, and
`position_information_processing`. It identifies a standard semantic role; it
is not inferred from a function ID, display name, exchange, description, or
declaration order. The profile DSL's reusable `required_capability_functions`
selector expresses role, applicable component kinds, required metadata,
per-Capability cardinality, and the optional position predicate.

For every declared Capability, the profile requires exactly one applicable,
Capability-owned function for each of the first three roles, with
`category: required` and `required_group: capability`.

## Position Information Processing decision

Task 026 records that black Section 3.3.1 prose calls Position Information
Processing a function that supports Capabilities, while its applicability is
conditional where a provided Capability depends on position information. The
source does not establish a Capability-owner reference or one function per
Capability. Accordingly, when any declared Capability has
`requires_position_information: true`, this profile requires exactly one
component-level Position Information Processing role, without requiring a
`function.capability` value. No function is required when all declared
Capabilities have the Boolean false.

## Exchanges and compatibility

Tasks 027–030 establish no universal Section 3.3 exchange minimum. This task
adds no exchange selectors or hidden exchange/name heuristics for position,
status, enable/disable, or operations.

The additive optional role field is compatible with v0.1: unrelated functions
need not have it, and contracts that omit Capability facts retain Task 031
behavior. Explicit facts make only the OMS profile enforce the new inventory.
