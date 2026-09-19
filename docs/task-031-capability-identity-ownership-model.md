# Task 031 — Portable Capability identity and ownership model

## Design basis and source boundary

Tasks 026–030 inspected the official OMS 2.5 Service Contract Template and
Instructions DOCX artifacts at upstream OMS revision
`726272bd0390982a759c91a9cf4e13b81c2b510b`. Their OOXML evidence establishes
that Section 3.3 applies to a Service or Subsystem that provides a Capability,
and that position information is conditional on a Capability's dependency. It
also establishes Capability-relative generic roles while treating editable
`[CapabilityName]` material and ESM/PO/POST rows as non-literal template
material. This task relies on those completed classifications and does not reopen
them or use upstream Markdown conversions as authority.

The prior v0.1 model could not safely enforce Section 3.3: it had no independent
fact for whether Capability data was supplied, whether there were zero, one, or
many Capabilities, the identity of each Capability, its position dependency, or
the owner of a function. Inferring those facts from function/exchange names would
make the parent condition circular and would turn source display material into
identity.

## Portable facts

Task 031 adds this optional portable representation:

```yaml
capabilities:
  - id: esm
    name: ESM
    requires_position_information: true
```

`id` uses the existing identifier grammar and is the local identity. `name` is a
non-empty human-readable display value, not an identity and not required to be
globally unique. `requires_position_information` is an explicit Boolean fact;
it is never inferred from exchanges, function names, UCI types, descriptions, or
other heuristics.

An omitted `capabilities` member means the portable contract did not supply
Capability facts. `capabilities: []` affirmatively declares zero Capabilities.
The schema has no default and consumers must retain this distinction for later
profile validation.

Functions may declare ownership explicitly:

```yaml
functions:
  - id: esm-operations
    name: ESM Capability Operations
    capability: esm
```

The reference is an ID, must resolve to a declared Capability, and is not parsed
or generated from a function name such as `ESM Capability Operations`. Functions
may omit it. The portable semantic validator rejects duplicate Capability IDs
with `SC_DUPLICATE_CAPABILITY` and unknown function references with
`SC_UNKNOWN_CAPABILITY`.

This is a portable representation of facts needed to apply already-classified
OMS rules; it does not claim the OMS DOCX itself contains a machine-readable
`capabilities` array.

## Deliberately deferred

Task 031 does not add OMS Section 3.3 profile enforcement. In particular it does
not add per-Capability required-function counts, conditional Position Information
Processing, Capability/Status, Enable/Disable, or Operations rules;
Capability-relative selectors; alternative-exchange semantics; response or other
behavior relationships; ESM/PO/POST rules; or function-name matching. Task 032
can use these independent facts for OMS-profile validation after the necessary
profile semantics are designed.

## Compatibility

The fields are additive within the experimental v0.1 grammar. Existing valid
v0.1 contracts that omit `capabilities` and `functions[].capability` remain
valid, and the OMS 2.5 profile remains unchanged. In particular, an ordinary
Service or Subsystem without a Capability declaration is not treated as having
affirmatively declared zero Capabilities and does not acquire new Section 3.3
profile failures.
