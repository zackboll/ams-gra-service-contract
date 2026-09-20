# RF FM Demod simulated owner responses

> **SIMULATED — ILLUSTRATIVE — NOT UPSTREAM EVIDENCE**
>
> These answers are simulated solely to demonstrate completion workflow closure.
> They are not statements from the RF FM Demod maintainers and must not be
> presented as upstream contract evidence.

This record answers every question in [RF FM Demod author questions](rf-fm-demod-author-questions.md).
It is human-readable input to the existing decisions, mapping, specific-function,
and Capability artifacts; it is not a machine-readable owner-response language.

## Service Initialization

- Function portable ID: `service-initialization`.
- FileMetadata: exchange ID `file-metadata`; topic `mission.file-metadata`.
- FileLocation: exchange ID `file-location`; topic `mission.file-location`.
- ServiceConfigFile: exchange ID `service-config-file`; protocol `https`; data
  type `ServiceConfigFile`; data format `application/json`; sharing pattern
  `request_response`.

## Service Status

- Function portable ID: `service-status`.
- ServiceStatus exchange ID: `service-status-report`.
- ServiceStatusDataRequest: ID `service-status-request`; topic
  `mission.service-status-request`.
- ServiceStatusDataRequestStatus: ID `service-status-request-status`; topic
  `mission.service-status-request-status`.

The published supporting evidence remains selected for the ServiceStatus topic
and nominal rate. OMS profile rules remain the source for its direction, mandate,
and timing kind. No response-time value is supplied.

## Specific Function topology and exchanges

- PositionReport and SignalReport belong to one illustrative Specific Function.
- Its tooling-only structural key is `fm-demod-processing`; it is **not** a
  portable function ID.
- Portable function ID: `rf-fm-demod-processing`; name: `RF FM Demod Processing`;
  applicability: `applicable`.
- PositionReport: exchange ID `position-report-input`; mandate `optional`; timing
  kind `asynchronous`. This mandate/timing classification is simulated author
  intent, not an inference from subscription behavior. Existing published
  candidates are selected for message, direction, and topic.
- SignalReport: exchange ID `signal-report-output`; mandate `mandatory`; timing
  kind `asynchronous`. This is an explicit simulated abstraction decision, not an
  inference from threshold-trigger prose or `report_rate_limit_hz`.

The observed SignalReport threshold trigger stays an observation. The observed
2.0 Hz rate limit remains implementation/runtime throttling, not portable timing
semantics, so neither is mapped into the contract.

## Capability inventory

The illustrative answer is explicitly zero portable OMS Capabilities. It becomes
`capabilities: []` in the completion Capability structure. This conclusion comes
from this simulated owner answer, **not** from runtime `capability_ids: []`, which
is insufficient evidence by itself.

Completion candidates are evidence observations. A valid contract does not need
to consume every observation.
