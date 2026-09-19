# Task 033 — Published OMS 2.5 Service Contract exercises

## Method and sources

This is an evidence exercise, not a claim that either project is noncompliant.
`PUBLISHED_CONTRACT` means the named primary contract; `PUBLISHED_SUPPORTING_DOC`
means a separate published project document; `IMPLEMENTATION` is not promoted to
contract semantics; `OMS_2_5_NORMATIVE` means the independent profile source; and
`NOT_STATED` means no evidence. Results use **ER** (explicit and representable),
**ENR** (explicit but not representable), **OMS** (required by OMS rather than
stated by contract), **NS** (not stated), **AC** (ambiguous/conflicting), and
**NA** (not applicable).

| Component | Pinned repository and revision | Primary contract | Supporting documents inspected |
| --- | --- | --- | --- |
| RF FM Demod | `https://github.com/open-arsenal/ams-gra-hello-world-sk-skills-rf-fm-demod`, `af13bd2926b15253e795920c91320733a29927ea` | `docs/compliance/oms-service-contract.md` | `docs/contracts.md`, addendum, checklist, configuration |
| Graupel | `https://github.com/open-arsenal/ams-gra-hello-world-sk-viz-graupel`, `c6b2b4d36c2d3258f3dda8ea0f98225e51abd7d4` | `docs/compliance/oms-service-contract.md` | isolator checklist, UCI ICD, contracts, configuration |

The independent normative comparison is `profiles/oms/2.5/profile.yaml`, sourced
from OMSC-INS-003 Rev M at OMS revision
`726272bd0390982a759c91a9cf4e13b81c2b510b`.

The authoring grammar models complete authored Service Contract semantics:
functions and OMS-message exchanges require category, applicability, direction,
mandate, topic, and timing. It is not currently an observation/extraction model
with first-class unknowns. These sources support considering separate concepts,
not weakening this grammar or adding `unknown` enum values.

## RF FM Demod field matrix

Primary locations are `oms-service-contract.md` sections 1, 3, 4.2--4.3, and 6.

| Area | Field | Evidence and provenance | Result |
| --- | --- | --- | --- |
| component | name | `RF FM Demod`, primary §§1/3; `PUBLISHED_CONTRACT` | ER |
| component | version | `1.0.0`, primary §1; `PUBLISHED_CONTRACT` | ER |
| component | kind | OMS Service/Data Processor, primary §§1/3 | ER (`service`; Data Processor has no v0.1 field) |
| standards | OMS version | v2.5, primary §1 | ER |
| standards | UCI version | v2.5, primary §2 | ER |
| capability | presence/absence known? | no portable Capability declaration; config `capability_ids` is implementation configuration | NS |
| function | identity, standard role, category, required group, applicability | no function rows; Initialization/Status independently required by §3.1 | NS / OMS |
| exchange | kind, selector/message/name, direction | PositionReport input; ServiceStatus and SignalReport outputs, primary §§4.2--4.3 | ER |
| exchange | mandate/LoM | absent for all three | NS |
| exchange | timing kind | ServiceStatus periodic; SignalReport condition-triggered; PositionReport absent | ER for ServiceStatus; ENR for event trigger; NS for PositionReport |
| exchange | numeric timing | keys named but no values; configuration supplies values as supporting/implementation evidence | NS in contract |
| exchange | topic | topic parameters named; values only in configuration examples | ENR |
| exchange | operational attribute / subscription group | absent | NS |
| Data Transfer | protocol/type/format/sharing | no Service Contract Data Transfer row | NA |
| traceability | source location | exact pinned primary locations above | ER |

**Conclusion:** RF FM Demod cannot be faithfully represented by current v0.1 from
its primary contract alone. Every named OMS-message row lacks LoM; PositionReport
lacks timing; SignalReport's event condition is not automatically `asynchronous`;
and topic values are absent. Required function entries and the profile-required
Initialization/Status request exchanges are also absent. Supporting documents give
topic examples and configured rates, but importing them changes provenance and
does not establish authored LoM or required-function metadata. An authoring
importer must not silently assert those values.

## Graupel field matrix

Primary locations are `oms-service-contract.md` sections 1, 3, 4.1--4.3, and 6;
the message list is corroborated, not replaced, by `uci-interaction-icd.md` §2.1.

| Area | Field | Evidence and provenance | Result |
| --- | --- | --- | --- |
| component | name | primary uses Graupel CZML Bridge Isolator and scope uses Bridge Service | AC (either nonempty v0.1 name is representable) |
| component | version | `1.0.0`, primary §1 | ER |
| component | kind | OMS Isolator, primary §1 | ER |
| standards | OMS version | v2.5, primary §1 | ER |
| standards | UCI version | v2.5, primary §2 | ER |
| capability | presence/absence known? | no Capability declaration | NS |
| function | identity, standard role, category, required group, applicability | no function rows; Initialization/Status independently apply | NS / OMS |
| exchange | kind, selector/message/name, direction | primary says UCI OMS Messages subscribed; ICD names 11 subscriptions | ER generic input; named selectors are supporting-doc evidence |
| exchange | mandate/LoM | absent | NS |
| exchange | timing kind / numeric timing | subscriptions absent; SystemStatus publication/frequency TBD | NS / AC for an implemented-publication claim |
| exchange | topic | configured topics are examples/configuration, not primary rows | NS in contract |
| exchange | operational attribute / subscription group | configuration exists outside primary; no portable values | NS |
| Data Transfer | protocol/type/format/sharing | LA-CAL WebSocket/JSON stated for OMS messages; no Data Transfer row/sharing pattern | ENR |
| traceability | source location | exact pinned primary/supporting locations above | ER |

**Conclusion:** Graupel cannot be faithfully represented by v0.1 from its primary
contract alone. It describes boundaries, not function/exchange rows. The primary
does not name subscribed UCI messages or provide topics, LoM, timing, or required
function metadata. The ICD supplies typical configured input messages, but not
complete portable rows. DIS and CZML are external-boundary traffic; v0.1 has no
boundary field and they must not be silently treated as OMS-facing exchanges. The
SystemStatus TBD does not conflict with the profile's distinct ServiceStatus rule;
it is insufficient evidence for that requirement.

## OMS profile comparison

Section 3.1 applies Service Initialization and Service Status to Services and
Isolators. The profile requires exact applicable required functions and
FileMetadata/FileLocation/ServiceConfigFile inputs (optional, asynchronous), plus
ServiceStatus output (mandatory, periodic), ServiceStatusDataRequest input
(mandatory, asynchronous), and ServiceStatusDataRequestStatus output (mandatory,
on-demand).

RF explicitly supports only periodic ServiceStatus output identity/direction. It
does not provide enough evidence for function metadata, LoM, profile timing shape,
or remaining exchanges. Graupel establishes Isolator status and OMS-boundary UCI
subscriptions, but no evidence for either required function or profile exchange.
Its SystemStatus TBD statement is not evidence about required ServiceStatus.
Neither published artifact is labelled categorically noncompliant merely for
incomplete evidence.

Recurring missing portable fields are function category/required group/
applicability, LoM, topic, classified timing, and numeric timing. OMS expects the
Section 3.1 functions and exchange shape; missing Markdown evidence does not prove
a component lacks them. Supporting documentation supplies some message, direction,
topic, and rate facts, but not a licence to import them as authored semantics.

## Section 3.3, resolver, and projection

RF's PositionReport and SignalReport names do not establish Capability provision.
Capabilities are omitted, so the profile correctly applies no Section 3.3
diagnostics. Isolators receive none even with Capability-like terms. Focused
regressions exercise both properties without document-specific validator rules.

Using pinned resolver manifest `uci-2.5-baseline` and UCI revision
`093610b7753944059360d3236770ab446d039556`, all named messages were **resolved**,
not unknown or ambiguous: PositionReport, ServiceStatus, SignalReport,
SystemStatus, SubsystemStatus, PositionReportDetailed, NavigationReport,
ObservationMeasurementReport, OperatorNotification, ESM_Activity, and PO_Activity.
No namespace syntax or type-layout parsing blocker was found. They were resolved
for this evidence exercise, not as exchanges in a new faithful fixture.

No real-world YAML fixture was added, so Inputs/Outputs projection was not run.
It requires a validated contract, and creating one would invent missing facts. The
projection could present authored rows and resolver identities, but cannot recover
absent source facts. Expected mismatches are source-document omissions and
external boundary-oriented organization, not a projection defect.

## Recommendation

Do not change the language now. Gather more published contracts and improve
source-document completion/import assistance that preserves provenance and asks an
author to confirm inferred/configuration values. If partial-document extraction
becomes a primary use case, design it as a separate observation model (or explicit
relationship to authored contracts), rather than weakening the complete authoring
grammar with undifferentiated `unknown` values.
