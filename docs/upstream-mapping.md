# Upstream Mapping: OMS Service Contract to v0.1

This document makes the mapping between the upstream OMS v2.5 Service Contract Instructions and the independent v0.1 machine-readable format explicit. It is intended to make reviews and future updates easier.

The primary upstream source for this mapping is **OMSC-INS-003 Rev M, Service Contract Template Instructions, 22 January 2026**. See `docs/references.md` for the official upstream artifact link.

This project is not authoritative; the upstream document wins if there is a conflict.

## 1. Function-level mapping

| Upstream concept | v0.1 representation | Notes |
|---|---|---|
| Function name | `functions[].name` | Human-readable name. |
| Function identity | `functions[].id` | Added by this format as a stable machine identifier. |
| Function category | `functions[].category` | `required` or `specific`, preserving the upstream minimum category distinction. |
| Required function family | `functions[].required_group` | Optional tool-friendly refinement: `service`, `subsystem`, `capability`. |
| Applicability / N/A tailoring | `functions[].applicability` | `applicable` or `not_applicable`. |
| N/A rationale | `functions[].not_applicable_reason` | Required by v0.1 when `not_applicable`. |
| Description | `functions[].description` | Informational in v0.1; no executable semantics. |
| Preconditions | Not formalized | Candidate future behavioral layer; prose is not silently converted to code contracts. |
| Reporting Interval | Partially represented through exchange timing where applicable | v0.1 does not claim to model the entire prose section. |
| Inputs and Outputs | `functions[].exchanges[]` | Core scope of v0.1. |
| Workflow and Orchestration | Not formalized | Candidate future state/behavior language. |
| Post Conditions | Not formalized | Candidate future behavioral layer. |
| Error Handling | Not formalized | Candidate future behavioral layer. |

The upstream instructions organize required functions into Required Service Functions, Required Subsystem Functions, and Required Capability-related Functions. `required_group` preserves that useful distinction without replacing the upstream organization.

## 2. Inputs/Outputs table mapping

The core v0.1 fields correspond directly to the upstream Inputs and Outputs table columns.

| OMS Service Contract column/concept | v0.1 | Ownership / behavior |
|---|---|---|
| Message Primitive (MP) | **Not stored** | Derived from UCI `PRIMITIVE_TYPE`. This avoids a duplicate source of truth. |
| Input / Output (I/O) | `direction` | `input` or `output`. |
| Data Exchange (DE) | `kind` | Explicit machine discriminator; see mapping below. |
| Data Exchange Name | `message` or `name` | `message` for OMS Message; `name` for other exchange kinds. |
| Data Exchange Information | `topic`, `operational_attribute`, `subscription_group`, or Data Transfer fields | Structured according to exchange kind. |
| Level of Mandate (LoM) | `mandate` | `mandatory` or `optional`. |
| Periodicity (P) | `timing.kind` | `asynchronous`, `on_demand`, `periodic`. |
| Nominal Response Time / Periodic Rate | timing numeric field | Preserved as **informative** metadata. |
| Max Response Time / Periodic Rate | timing numeric field | Preserved as **informative** metadata. |
| Appendix C Mapping | `appendix_c_mapping` | Optional document-generation/traceability token for OMS Message exchanges. |

## 3. Message Primitive is intentionally derived

The upstream instructions state that the Message Primitive column corresponds to the `PRIMITIVE_TYPE` tag annotation in the UCI schema message definitions file.

Therefore this is intentionally invalid as a design pattern:

```yaml
message: ServiceStatus
primitive: Data-1
```

Instead, a consuming resolver performs:

```text
ServiceStatus
    |
    v
selected UCI schema
    |
    +--> message definition
    |
    +--> PRIMITIVE_TYPE
    |
    v
resolved primitive
```

This prevents the service contract and UCI schema from disagreeing about the same standardized fact.

## 4. I/O direction

Upstream I/O values are Input (`I`) and Output (`O`). v0.1 expands these into readable strings:

```yaml
direction: input
```

or:

```yaml
direction: output
```

The upstream instructions explicitly require two unique table rows when the same message is used as both input and output. v0.1 preserves this by requiring one direction per exchange object.

Correct:

```yaml
exchanges:
  - id: foo-input
    kind: oms_message
    direction: input
    # ...

  - id: foo-output
    kind: oms_message
    direction: output
    # ...
```

There is intentionally no `direction: input_output` value.

## 5. Data Exchange kinds

The upstream Inputs/Outputs table uses the following DE codes and one meaningful blank case:

| Upstream table | v0.1 `kind` |
|---|---|
| `M` — OMS Message | `oms_message` |
| `DT` — Data Transfer | `data_transfer` |
| `SS` — Special Signal | `special_signal` |
| `SE` — Security Exchange | `security_exchange` |
| blank — Non-OMS Message | `non_oms_message` |

The explicit `non_oms_message` discriminator is deliberate. A semantically meaningful blank works in a human table, but it is a poor machine-language discriminator.

## 6. OMS Message mapping

For `kind: oms_message`, v0.1 requires:

```yaml
message: ServiceStatus
topic: ServiceStatus
```

The upstream instructions say Data Exchange Name is the specific OMS Message name and Data Exchange Information includes the specific topic on which the message is published.

If the Service Contract identifies non-default CAL operational attributes or a subscription group, v0.1 can represent them separately:

```yaml
topic: ServiceStatus
operational_attribute: SOAC-1
subscription_group: ExampleGroup
```

This avoids parsing bracket syntax such as `Topic [SOAC-1]` after ingestion.

## 7. Data Transfer mapping

The upstream instructions describe Data Transfer exchange information using:

```text
Protocol Name [Data Type, Data Format, Sharing Pattern]
```

v0.1 normalizes these into distinct fields:

```yaml
kind: data_transfer
name: Example Transfer
protocol: ExampleProtocol
data_type: ExampleType
data_format: ExampleFormat
sharing_pattern: ExamplePattern
```

v0.1 does not define the external protocol/data-format vocabularies. It preserves the Service Contract values for downstream tooling.

## 8. Non-OMS Message mapping

For a Non-OMS Message, the upstream DE cell is blank, the Data Exchange Name is expected to match the Non-OMS Messages section, and the DE Information cell is left blank.

v0.1 converts the implicit blank into an explicit kind:

```yaml
kind: non_oms_message
name: ExampleLegacyMessage
reference: Non-OMS Messages table entry
```

No topic is required because that would add semantics not present in the upstream DE Information rule for this case.

## 9. Level of Mandate

Upstream meanings are preserved:

```yaml
mandate: mandatory
```

means the Service cannot perform the functionality without that input/output.

```yaml
mandate: optional
```

means the input/output enhances execution of the function but is not required for normal operation.

This field is **function-level interface semantics**, not a safety criticality level and not automatically a compile-time/proof rule.

## 10. Periodicity/timing mapping

| Upstream | v0.1 |
|---|---|
| `A` — Aperiodic / Asynchronous | `timing.kind: asynchronous` |
| `OD` — On Demand | `timing.kind: on_demand` |
| `P` — Periodic | `timing.kind: periodic` |

On-demand values:

```yaml
timing:
  kind: on_demand
  nominal_response_seconds: 0.5
  max_response_seconds: 3.0
```

Periodic values:

```yaml
timing:
  kind: periodic
  nominal_rate_hz: 1.0
  max_rate_hz: 0.5
```

The upstream v2.5 instructions label the nominal/max response/rate columns **informative (not normative)**. v0.1 therefore preserves the values but does not upgrade them to deadlines or proof obligations.

Notably, consumers should not invent an ordering validation between `nominal_rate_hz` and `max_rate_hz`: the format records the source table values as values, without reinterpreting the table's terminology.

## 11. Required Service Functions and profile validation

The upstream Service Contract instructions say Required Service Functions are required for OMS Services and include Service Initialization and Service Status, with stated tailoring/applicability rules for other component types.

The portable v0.1 JSON Schema does **not** hard-code the OMS 2.5 function catalog. Instead, a future OMS profile validator should operate conceptually as:

```text
contract_version 0.1  ---> syntax/portable semantic validation
oms_version 2.5       ---> OMS 2.5 function/profile validation
service.kind          ---> applicability/tailoring checks
```

This keeps the portable grammar independent from a particular OMS release while still allowing strict OMS-aware validation.

## 12. Workflow and formal behavior are intentionally deferred

The upstream Service Contract includes Workflow and Orchestration sections and can use sequence diagrams/state information. These are important, but v0.1 does not pretend that arbitrary prose or PlantUML is a formal program contract.

A future machine behavior language could support concepts such as:

```yaml
behavior:
  on: settings-command-input
  require:
    - state: normal
  produce:
    - settings-command-status-output
```

Only a future version with precise event/order/state/error semantics should make such a model normative or generate SPARK contracts from it.

## 13. AMS GRA mapping boundary

This repository deliberately references, but does not redefine, AMS GRA architecture volumes. The intended relationship is:

```text
AMS GRA architecture
  |
  +-- Service MPU / OMS Service MPU context
  +-- Software Architecture context
  +-- MASI context
           |
           v
OMS Service Contract semantics
           |
           v
this machine-readable companion
           |
           +--> UCI-aware code generation
           +--> deployment projection
           +--> tests
           +--> documentation
```

MEL/MFA interfaces and Skill composition are not forced into the v0.1 Service Contract model. If those need a machine-readable composition specification later, that may warrant a distinct artifact rather than overloading this one.
