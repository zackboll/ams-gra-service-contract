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
Required Subsystem Function inventory, Subsystem Status exchange surface, and
the completed Startup, State Command Processing, BIT, Calibration, Shutdown,
and Required Capability-related Function source classifications.

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

**Subsystem Startup** (Section 3.2.1 and Table 3.2-1) has no profiled exchange
minimum. Every matcher-owned cell for `FileMetadata`, `FileLocation`,
`Subsystem_OFP`, `SubsystemConfigFile`, and `MDF` resolves to green `00B050` in
the pinned official DOCX. The NFS/FTP statement, all three MDF-information
examples, and the instruction to keep one applicable example and remove the
others are green guidance too. Thus `FileMetadata`/`FileLocation` are not
reused from Service Initialization, the configuration-file and direct-MDF cases
are not conflated, and `QueryDataRequest`/`QueryDataRequestStatus` from Example
3 are not profile rules. Optional LoM is not row-presence logic; the applicable
Startup fixture has zero source-backed exchanges because all candidate fields
are removable guidance. No fixed alternative-set relationship is established,
so no profile-model extension is justified.

**Subsystem Built-In Test (BIT)** (Section 3.2.4 and Table 3.2-4) also has no
profiled exchange minimum. All seven substantive candidate rows
(`SubsystemBIT_Status`, `SubsystemBIT_Configuration`,
`SubsystemStateCommand`, `SubsystemStateCommandStatus`,
`SubsystemBIT_Command`, `SubsystemBIT_CommandStatus`, and `Log_File`) resolve
to green `00B050` in the official DOCX for every field the profile matches.
They are removable guidance, and the message-specific workflow prose is green
as well. This is independently classified from State Command Processing;
neither optional LoM nor numeric `1 Hz`/`0.5 sec`/`3 sec` timing is used to
decide row presence or profile matching. An applicable BIT fixture therefore
needs no source-backed exchanges; a permitted `not_applicable` BIT still
requires rationale and zero exchanges under portable validation.

**Subsystem Calibration** (Section 3.2.5 and Table 3.2-5) has no profiled
exchange minimum. Every matcher-owned cell for all seven substantive rows
(`SubsystemCalibrationStatus`, `SubsystemCalibrationConfiguration`,
`SubsystemStateCommand`, `SubsystemStateCommandStatus`,
`SubsystemCalibrationCommand`, `SubsystemCalibrationCommandStatus`, and
`Log_File`) resolves to green `00B050` in the pinned official DOCX. The
message-specific workflow prose is green guidance as well. This classification
is independent of State Command Processing: no Calibration row inherits that
section's fixed command rule. Optional LoM does not permit omitting a fixed row;
these rows are unprofiled because their matched source fields are removable
guidance. Numeric `1 Hz`, `0.5 sec`, and `3 sec` values remain informative and
are not profile-enforced. An applicable Calibration fixture therefore needs no
source-backed exchanges, and permitted `not_applicable` Calibration still
requires rationale and zero exchanges under portable validation.

**Subsystem State Command Processing** (Section 3.2.3 and Table 3.2-3) has one
profiled minimum: `SubsystemStateCommand` as OMS-message input, mandatory, and
asynchronous. Although the complete row is mixed because its Appendix C cell is
green, every field matched by that rule is fixed black/automatic, and fixed
workflow prose corroborates receipt of the command. The profile does not match
Appendix C.

`SubsystemStateCommandStatus` is intentionally not profile-enforced. Its fixed
table direction is input while fixed workflow prose says the Subsystem responds
with it; the profile does not guess either status direction. Its green timing
and Appendix C cells are also not matched. The conditional `not_applicable`
form skips this command exchange rule only when `not_applicable` is allowed by
the requirement; portable validation still requires its rationale and zero
exchanges.

Additional valid exchange rows are allowed. The profile intentionally does not
fix Service Initialization Data Transfer protocol, data type, data format, or
sharing pattern; nor does it fix topics, operational attributes/SOAC selection,
subscription groups, numerical timing values, Appendix C content, contract
traceability, or UCI message primitives. All Section 3.2 Required Subsystem
Function exchange surfaces now have an explicit source-classification outcome:
Startup, BIT, Calibration, and Shutdown have no fixed minimum; Subsystem Status
has its three fixed shapes; and State Command Processing has a fixed command
minimum plus a documented status-direction conflict.
Required Capability-related Function source semantics are classified, but exact
per-Capability inventory validation is deferred because v0.1 has no explicit
Capability identity/presence model. Section 3.3 applies to Capability-providing
Services and Subsystems, excludes Isolators, and makes Position Information
Processing conditional on a Capability's position dependency. The profile has
no independent facts for any of those conditions, cannot associate arbitrary
function names with a Capability, and deliberately does not infer them from
names or existing capability-group functions. The source's `[CapabilityName]`
replacement and copy-for-each-Capability instructions are green template
guidance; no literal placeholder or name-pattern rule is encoded. See
[Task 026 evidence](task-026-oms25-capability-function-inventory.md).

Task 027 classifies Position Information Processing Table 3.3-1 separately.
Both `PositionReport` and `PositionReportDetailed` rows have green guidance for
every profile-matched field (kind, message, direction, LoM, and timing kind);
their black Appendix C cells are not profile fields. Fixed black Description and
Workflow prose conceptually names periodic incoming `PositionReport` or
`PositionReportDetailed`, but does not establish a machine-checkable cardinality
or individual mandatory shape. The green row-selection and example workflow
instructions are removable authoring guidance. No Position Information function
or exchange rule is profile-enforced: v0.1 also lacks the independent Capability
and position-dependency facts needed to condition such a function. If future
evidence establishes a fixed alternative group, v0.1 would additionally need a
deliberately designed conditional-function and alternative-exchange model rather
than encoding OR as an all-required list. See [Task 027 evidence](task-027-oms25-position-information.md).

Task 028 classifies Capability and Capability Status Table 3.3-2 separately.
Its `ESM_Capability` and `ESM_CapabilityStatus` rows are removable green
examples in every matcher-owned field, including DE and LoM. Mixed generic
function/Description prose fixes Capability-relative publication/output and
periodic behavior, but the green `[CapabilityName]` replacement means it is not
an exact selector; kind and mandate are not fully fixed. v0.1 has no independent
Capability identity or function ownership from which to instantiate the family,
so no ESM, literal placeholder, or name-template profile rule is encoded. See
[Task 028 evidence](task-028-oms25-capability-status.md).

Task 029 classifies Capability Enable/Disable Table 3.3-3 separately. Its
`ESM_SettingsCommand` and `ESM_SettingsCommandStatus` rows are removable green
examples in every matcher-owned field, including DE, LoM, and Periodicity.
Mixed Description/Workflow prose fixes only a Capability-relative
`SettingsCommand` input family and `SettingsCommandStatus` output/response
family. It does not fix portable kind, mandate, or an OMS timing discriminator;
the response relationship is behavioral rather than `on_demand` evidence. v0.1
has neither Capability identity/ownership for exact family instantiation nor a
response-pair model, so no ESM, literal placeholder, name-template, or partial
exchange profile rule is encoded. See
[Task 029 evidence](task-029-oms25-capability-enable-disable.md).

Task 030 completes the Section 3.3 exchange-table classification with Capability
Operations Table 3.3-4. `Entity` and `SignalReport` are explicitly green ESM
examples; `ProductMetadata`, `ProductLocation`, and `ImageFile` are explicitly
green PO/POST examples. Every matcher-owned row field is removable guidance;
for `ImageFile`, DE=`DT`, protocol `NFS`, type `Image`, format `JPEG`, sharing
`Shared Use`, and Appendix C `TBD` are green example values too. Mixed generic
heading/Description prose identifies only a Capability Operations role, while
fixed Preconditions remain behavioral and the Reporting Interval guidance does
not establish timing. No row is universal, no domain-specific group is
profile-enforced, and no selector/name heuristic is used. See
[Task 030 evidence](task-030-oms25-capability-operations.md).

The profile also does not validate conditional Section 3.1 Service Functions for
Platform-hosted Adapters or other OMS-version profiles. It does not claim full
OMS Subsystem compliance.

## Partial reference examples

Files in `examples/` can be intentionally partial, source-backed function
demonstrations. Ordinary v0.1 validation does not mean OMS profile completeness.
For example, `examples/service-status.yaml` and
`examples/service-initialization.yaml` are valid, source-backed v0.1 fragments
but are not complete OMS Service contracts. Under the whole-service OMS 2.5
profile each fails only for the other required function.

Future profiles can evolve independently for OMS 2.6 or additional conformance
rules without changing the portable v0.1 grammar.
