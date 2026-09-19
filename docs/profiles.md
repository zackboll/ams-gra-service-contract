# Profile validation

The v0.1 service-contract schema is a portable grammar, not an OMS-version
conformance checklist. `contract_version`, OMS version, UCI version, and a
profile version are independent. OMS-specific requirements therefore live in
opt-in, machine-readable profile manifests rather than in
`schema/v0.1/service-contract.schema.json`.

## OMS 2.5 required-function profile

`profiles/oms/2.5/profile.yaml` is profile format version `0.1`, profile ID
`oms-2.5`, and supports contract version `0.1`. Its source is OMSC-INS-003
Rev M, *OMS Service Contract Instructions v2.5*, dated 2026-01-22, pinned to
upstream OMS commit `726272bd0390982a759c91a9cf4e13b81c2b510b`.

Current OMS 2.5 coverage includes the Required Service Function inventory,
Service Initialization exchange surface, Service Status exchange surface,
Required Subsystem Function inventory, and Subsystem Status exchange surface.

Section 3.1 says every OMS Service must provide the Required Service Functions
and that the section also applies to Isolators. Sections 3.1.1 and 3.1.2 say
that **Service Initialization** and **Service Status**, respectively, are
required for Services and Isolators. The profile consequently requires exactly
one function with each exact name for `service` and `isolator`, with
`category: required`, `required_group: service`, and
`applicability: applicable`.

Section 3.2 says every OMS Subsystem must provide the Required Subsystem
Functions and that the section is required for Subsystems (Services and
Isolators mark it Not Applicable). The profile therefore requires exactly one
function by each canonical name for `subsystem`: **Subsystem Startup**,
**Subsystem Status**, **Subsystem State Command Processing**, **Subsystem
Built-In Test (BIT)**, **Subsystem Calibration**, and **Subsystem Shutdown**.
All have `category: required` and `required_group: subsystem`.

Required inventory/section presence is not always `applicability: applicable`.
Startup, Status, and Shutdown must be applicable. State Command Processing,
BIT, and Calibration remain required inventory entries, but each permits either
`applicable` or `not_applicable`; ordinary v0.1 validation requires a non-empty
`not_applicable_reason` and zero exchanges for the latter. The profile format
expresses that narrow conditional rule with `allowed_applicability`, mutually
exclusive with scalar `applicability`.

Section 3.1 Service Function applicability for Subsystems remains conditional
on Platform-hosted Adapter facts unavailable in v0.1 contracts; this profile
does not infer it.

Use it explicitly:

```bash
python tools/validate.py \
  --profile profiles/oms/2.5/profile.yaml \
  my-complete-service.yaml
```

The validator rejects unsupported contract versions and OMS-version mismatch
before treating the profile as applicable. It matches standard functions by
their exact upstream canonical `function.name`, not local `function.id` or
traceability prose. A future contract version may introduce explicit
standard-function identity if real consumers show that name matching is
insufficient.

For the uniquely matched required functions, the profile additionally requires
these minimum exchange shapes, regardless of local function/exchange IDs or
declaration order:

**Service Initialization** (Table 3.1-1):

- `FileMetadata`: OMS-message input, optional, asynchronous;
- `FileLocation`: OMS-message input, optional, asynchronous; and
- `ServiceConfigFile`: Data Transfer input, optional, asynchronous.

The official table presents these as black-text rows. Per the Section 3 table
instructions, black-text message rows cannot be removed; `optional` is the
Level of Mandate for function execution, not permission to omit the profile row.

**Service Status** (Table 3.1-2):

- `ServiceStatus`: output, mandatory, periodic;
- `ServiceStatusDataRequest`: input, mandatory, asynchronous; and
- `ServiceStatusDataRequestStatus`: output, mandatory, on-demand.

**Subsystem Status** (Section 3.2.2 and Table 3.2-2):

- `SubsystemStatus`: OMS-message output, mandatory, periodic;
- `SubsystemStatusDataRequest`: OMS-message input, mandatory, asynchronous; and
- `SubsystemStatusDataRequestStatus`: OMS-message output, mandatory, on-demand.

**Subsystem Shutdown** (Section 3.2.6 and Table 3.2-6) has no profiled
exchange minimum. The pinned official DOCX's three substantive rows
(`SubsystemStateCommand`, `SubsystemStateCommandStatus`, and `Log_File`) use
the `Table*Green` paragraph styles. Those styles explicitly set OOXML
`w:color/@w:val` to `00B050`, so all three are removable green guidance/example
content under the template instructions, rather than fixed black rows. This is
why `Log_File` is not a profile rule: its `optional` LoM was not interpreted as
permission to omit a fixed row; the independently established green source
classification excludes the entire row from the portable minimum.

The green guidance shows `SubsystemStateCommand` as input, mandatory, and
asynchronous, and `SubsystemStateCommandStatus` as output, mandatory, and
on-demand, with informative 0.5/3-second response values. If a program uses
those exchanges, Table 3.2-6's status output direction is the relevant
Section 3.2.6 evidence, rather than the conflicting Table 3.2-3 input row.
None of those message shapes or timing numbers is profile-enforced because the
rows are removable guidance.

**Subsystem State Command Processing** (Section 3.2.3 and Table 3.2-3) has no
profiled exchange minimum. Its command and status shape cells are fixed
black/automatic OOXML content, but the command Appendix C cell and the status
timing/Appendix C cells are green guidance, so both rows are mixed. More
importantly, the fixed table marks `SubsystemStateCommandStatus` as input while
the fixed workflow prose says the Subsystem responds with it. The profile does
not guess a status direction from that conflict. An applicable function may
therefore have `exchanges: []`; its permitted `not_applicable` form still needs
the portable rationale and zero exchanges.

Additional valid exchange rows are allowed. The profile intentionally does not
fix Service Initialization Data Transfer protocol, data type, data format, or
sharing pattern; nor does it fix topics, operational attributes/SOAC selection,
subscription groups, numerical timing values, Appendix C content, contract
traceability, or UCI message primitives. The remaining unclassified Section 3.2
exchange surfaces are Subsystem Startup,
BIT, and Calibration; State Command Processing was classified with no fixed
exchange minimum.
The profile also does not validate Required Capability-related Function
inventory, conditional Section 3.1 Service Functions for Platform-hosted
Adapters, or other OMS-version profiles. It does not claim full OMS Subsystem
compliance.

## Partial reference examples

Files in `examples/` can be intentionally partial, source-backed function
demonstrations. Ordinary v0.1 validation does not mean OMS profile completeness.
For example, `examples/service-status.yaml` and
`examples/service-initialization.yaml` are valid, source-backed v0.1 fragments
but are not complete OMS Service contracts. Under the whole-service OMS 2.5
profile each fails only for the other required function.

Future profiles can evolve independently for OMS 2.6 or additional conformance
rules without changing the portable v0.1 grammar.
