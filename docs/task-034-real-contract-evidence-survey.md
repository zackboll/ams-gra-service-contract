# Task 034 — Broadened published OMS 2.5 contract evidence

This extends [Task 033](task-033-real-service-contract-exercises.md). This is
an evidence exercise, not a compliance finding. `PUBLISHED_CONTRACT` is the
primary Service Contract and `PUBLISHED_SUPPORTING_DOC` is another published
document/configuration. `IMPLEMENTATION` remains separate. Results use **ER**,
**ENR**, **OMS**, **NS**, **AC**, and **NA** as defined by Task 033.

| Component | Pinned repository and revision | Primary / supporting evidence inspected |
| --- | --- | --- |
| IR Search and Track | `open-arsenal/ams-gra-hello-world-sk-skills-ir-search-and-track` `7d06735e56aa0baa8cc61e578928ee4d28936bc3` | `docs/compliance/oms-service-contract.md`; contracts, configuration, checklist, addendum |
| Supercell | `open-arsenal/ams-gra-hello-world-sk-sim-supercell` `0687e68278f3f2a421ff7cc846dbd1014bbf7798` | primary; contracts, configuration, UCI ICD, checklist, addendum |
| Squall OMS Adapters | `open-arsenal/ams-gra-hello-world-sk-sensors-squall` `b1015728f904c799fa0c07489fce48e78f67845f` | primary; contracts, configuration, architecture, checklist, addendum |

## IR Search and Track

Primary §§1--4.3 and 6 identify version 1.0.0, an OMS **Service**, OMS/UCI
v2.5, and `Skill / Data Processor`. This is **ER** for `service.kind: service`;
the latter label has no portable kind meaning. `PositionReport` input, periodic
`ServiceStatus` output, and target-detection `ObservationMeasurementReport`
output are **ER** selector/direction evidence. Periodic is representable;
“when targets are detected” is **ENR**, not an authored timing classification.

| Area | Evidence and result |
| --- | --- |
| capabilities | No explicit inventory or explicit none: **NS**. IR and message names are not Capability facts. |
| functions | No identity, role, category, group, or applicability rows: **NS**; Service functions are independently **OMS**. |
| exchanges | Selectors/directions **ER**; LoM and operational/subscription group **NS**. |
| timing/topic | Status periodic **ER**; numeric rate **NS**. Configuration gives concrete topics and `status_report_rate_hz` as supporting candidates. |
| Data Transfer/boundary | LA-CAL/OWP is **ENR** for a complete Data Transfer row. MEL frame and process lifecycle are external boundaries. |
| traceability | Primary §§1--4.3 and 6 at the pinned revision: **ER**. |

**Faithful YAML:** no, primary-only or combined. Support makes topics, numeric
rate, and trigger detail concrete, but not LoM, function metadata, or the
detection output's OMS timing classification.

## Supercell

Primary §§1--4.3 and 6 give version 1.0.0, OMS/UCI v2.5, and a **Service**;
`Core Simulation` is not a portable kind. Periodic `SystemStatus`,
`PositionReport`, `NavigationReport`, and `RoutePlan` outputs are **ER** for
selector/direction. LoM, function metadata, operational attributes, and numeric
values are **NS**. No explicit Capability facts or explicit none exists:
**NS**; navigation/simulation labels and message names are not Capability facts.

FlightGear/`FGNetCtrls` UDP, DIS, JSBSim, TOML scenario input, CLI/process
lifecycle, and Prometheus are external process/runtime interfaces. They are not
OMS-facing portable-contract exchanges. Published contracts, configuration, and
UCI ICD supply candidate topics/rates but do not alter this boundary.

| Area | Evidence and result |
| --- | --- |
| functions | No identity, role, category, group, or applicability: **NS**; Service functions are **OMS**. |
| exchanges | Four UCI output selectors/directions: **ER**; LoM/group: **NS**. |
| timing/topic | Periodic prose is **ER** where stated; `position_hz`/`prd_hz` are not numeric values. Supporting documents provide candidate topic/rate evidence. |
| Data Transfer/traceability | LA-CAL/OWP is **ENR** for a complete Data Transfer row; pinned primary §§1--4.3 and 6 are **ER** traceability. |

`SystemStatus` differs from the independent Service Status selector
`ServiceStatus`; this is evidence difference, not a compliance verdict.
`ServiceStatusDataRequest` evidence is not demonstrated, which does not prove
the implementation lacks it. **Faithful YAML:** no, primary-only or combined.

## Squall OMS Adapters

Primary §§1--4.3 and 6 give Service Name `Squall MFA OMS Adapter Service`,
version 1.0.0, OMS/UCI v2.5, and Service Class `Hardware Abstraction /
Subsystem Status`. Scope/lifecycle call the adapters OMS Service
interfaces/services. Explicit architectural evidence therefore supports
**service**, not subsystem or isolator. `SubsystemStatus` publication and the
wrapped MFA backend are function/exchange evidence, not component identity.

| Area | Evidence and result |
| --- | --- |
| capabilities | No explicit inventory or explicit none: **NS**. MFA and `SubsystemStatus` are not Capability facts. |
| functions | No identity, role, category, group, or applicability rows: **NS**; Service functions are **OMS**. |
| exchanges | Periodic `ServiceStatus` and `SubsystemStatus` outputs: selector/direction/timing **ER**; LoM/group **NS**. |
| timing/topic | Primary parameter names have no values: **NS**. Published configuration provides candidate topics/rate. |
| Data Transfer/boundary | OWP is **ENR** for Data Transfer. In-process MEL/backend hardware is an external boundary. |
| traceability | Pinned primary §§1--4.3 and 6: **ER**. |

**Faithful YAML:** no, primary-only or combined. Supporting documents clarify
OWP status publication, topics/rate, JSON payloads, and MEL boundary, but not
LoM or function/profile metadata. No YAML fixture is added.

## Five-contract synthesis

This combines the new evidence with RF FM Demod and Graupel from Task 033.
Counts require enough information in the *primary published Service Contract*
without inference; a partial statement does not count.

| Portable field | Primary coverage of 5 | Supporting-only additional | Pattern |
| --- | ---: | ---: | --- |
| component kind | 5 | 0 | Explicit architecture determines kind, never messages. |
| OMS version / UCI version | 5 / 5 | 0 / 0 | Consistently explicit. |
| function identity / category / group / applicability | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 | Systemically absent. |
| message selector / direction | 4 / 4 | 1 / 1 | Graupel named selectors are supporting evidence. |
| mandate / LoM | 0 | 0 | Systemically absent. |
| timing kind | 1 | 2 | Event prose is not silently classified. |
| numeric timing | 0 | 4 | Configuration commonly supplies rates, not authored timing semantics. |
| topic value | 3 | 2 | Richer documents/configuration commonly supply concrete topics. |
| Capability presence | 0 | 0 | No explicit Capability facts. |

Richer support provides message identity/direction, topic, numeric rate, and
event-trigger detail. Across all five it still fails to provide LoM, OMS
function association, function category, required group, applicability, or
normative timing classification. This favors author-assisted completion, not a
weakened complete authored-contract grammar.

## OMS profile and UCI resolver comparison

The independent OMS 2.5 profile classifies Service identity/application as
**demonstrated** for RF, IR, Supercell, Squall and Isolator for Graupel.
Required Service function metadata is **not demonstrated** for all. ServiceStatus
output is demonstrated for RF, IR, Squall; not demonstrated for Graupel; and
has explicit selector difference (`SystemStatus`) for Supercell. Request/status
request evidence is not demonstrated for all. No source has an explicit profile
conflict. Subsystem requirements are **not applicable** to explicitly
non-subsystem components; Squall's SubsystemStatus does not alter that.
Not demonstrated is not a noncompliance conclusion.

Using `uci-2.5-baseline` at UCI revision
`093610b7753944059360d3236770ab446d039556`, all new selectors resolved uniquely:
`PositionReport`, `ServiceStatus`, `ObservationMeasurementReport`,
`SystemStatus`, `NavigationReport`, `RoutePlan`, and `SubsystemStatus`.
None was unknown or ambiguous; no namespace-qualified syntax is needed.

## Task 035 decision — Direction A

Choose **A: authoring/completion assistant**. Five artifacts from one ecosystem
are meaningful, but not the 1.0 independent-consumer criterion. The grammar is
appropriate; primary contracts are incomplete; and supporting material provides
candidate values authors must confirm before they become contract semantics. A
future worksheet can retain field, observed candidate, source, and provenance
without emitting a valid contract. This task adds no importer, observation
schema, core `unknown`, weakened semantics, Capability inference, or
component-kind inference.
