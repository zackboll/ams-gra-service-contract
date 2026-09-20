# RF FM Demod simulated owner answer-loop

> **SIMULATED — ILLUSTRATIVE — NOT UPSTREAM EVIDENCE**
>
> The materialized YAML in this tutorial is not an official RF FM Demod Service
> Contract. It is a valid portable contract produced from real published evidence
> plus explicitly labelled simulated owner responses.

The [RF FM Demod completion exercise](rf-fm-demod-completion-exercise.md) starts
with pinned published evidence and deliberately fails closed. This companion
exercise demonstrates what happens after an owner answers the open questions. No
tool generates those answers; the simulated human response record does.

## 1. Start with the incomplete evidence workspace

```bash
python tools/completion.py scaffold examples/completion/rf-fm-demod-workspace.yaml
python tools/completion.py check examples/completion/rf-fm-demod-workspace.yaml
```

The scaffold has 16 unresolved local fields and `check` reports
`CA_MATERIALIZATION_INCOMPLETE`. Read the concrete questions in
[RF FM Demod author questions](../examples/rf-fm-demod-author-questions.md).

## 2. Receive labelled simulated answers

For this exercise there is no actual maintainer response. The complete response
record is [simulated owner responses](../examples/rf-fm-demod-simulated-owner-responses.md),
prominently labelled simulated, illustrative, and not upstream evidence.

It supplies local IDs, topics, transfer metadata, Specific Function ownership,
mandates/timing, and the explicit zero-Capability decision. It also explicitly
declines to map SignalReport's threshold trigger and 2.0 Hz implementation rate
limit into portable semantics.

## 3. Translate answers into existing artifacts

The response is represented without a new schema:

- `rf-fm-demod-owner-confirmed-decisions.yaml` uses `select_candidate` for
  published evidence and `value` for simulated owner choices;
- `rf-fm-demod-owner-confirmed-specific-functions.yaml` declares the chosen
  topology; its `fm-demod-processing` key is tooling-only, never a portable ID;
- `rf-fm-demod-owner-confirmed-capabilities.yaml` declares `capabilities: []`;
- `rf-fm-demod-owner-confirmed-mapping.yaml` attaches all decisions to existing
  typed destinations; and
- `rf-fm-demod-owner-confirmed-workspace.yaml` combines those artifacts with the
  unchanged RF evidence and OMS profile.

Published candidates stay unchanged. Completion candidates are evidence
observations: a valid contract does not need to consume every observation.

## 4. Compare evidence and profile, then scaffold again

```bash
python tools/completion.py profile-evidence \
  examples/completion/rf-fm-demod-owner-confirmed-workspace.yaml
python tools/completion.py scaffold \
  examples/completion/rf-fm-demod-owner-confirmed-workspace.yaml
```

Profile-evidence remains pre-materialization evidence comparison: its ServiceStatus
selector, direction, and timing-kind facts remain `all_aligned`. It does not use
owner-only values and does not establish conformance. The completed scaffold has
no unresolved required fields and no unmapped author decisions.

The original workspace omits capabilities (unknown/not supplied). The simulated
workspace explicitly emits `capabilities: []` (zero declared). It therefore has
no OMS Section 3.3 Capability functions.

## 5. Materialize and validate

```bash
python tools/completion.py check \
  examples/completion/rf-fm-demod-owner-confirmed-workspace.yaml
python tools/completion.py materialize \
  examples/completion/rf-fm-demod-owner-confirmed-workspace.yaml \
  --format yaml --output /tmp/rf-fm-demod-simulated-contract.yaml
python tools/validate.py --profile profiles/oms/2.5/profile.yaml \
  /tmp/rf-fm-demod-simulated-contract.yaml
```

`check` succeeds. Materialization validates portable `SC_*` rules and OMS `OP_*`
rules before output; the standalone validation repeats both checks. In contrast,
profile-evidence is informational candidate/profile alignment.

The resulting inventory is Service Initialization (required), Service Status
(required), and RF FM Demod Processing (specific). The specific function contains
PositionReport input/optional/asynchronous and SignalReport
output/mandatory/asynchronous. No trigger or rate-limit observation appears.

For manual downstream testing only, this richer-shaped simulated fixture can be
handed to OMS-codegen; this repository does not depend on or run OMS-codegen:

```bash
ams-gra-codegen-oms service-plan \
  --contract /tmp/rf-fm-demod-simulated-contract.yaml \
  --schema /path/to/UCI_MessageDefinitions_v2_5_0.xsd
```

## Ownership and provenance

| Final field | Owner/source |
| --- | --- |
| Service name, version, OMS/UCI/AMS GRA version | selected published evidence |
| ServiceStatus direction, mandate, timing kind | OMS profile |
| ServiceStatus topic and rate | selected supporting evidence |
| ServiceStatus ID and request/status IDs/topics | simulated owner |
| PositionReport message, direction, topic | selected published evidence |
| PositionReport mandate, timing, ID | simulated owner |
| SignalReport message, direction, topic | selected published evidence |
| SignalReport mandate, timing, ID | simulated owner |
| Capabilities `[]` | simulated owner |

Thus scaffold provenance retains candidate/source/provenance for selected fields,
uses `author_decision` without fabricated candidate provenance for simulated
values, and retains `oms_profile` for fixed OMS semantics.
