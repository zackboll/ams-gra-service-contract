# Completion Assistant walkthrough

## Recommended workspace workflow

The recommended front door is `tools/completion.py`; the individual completion
tools remain useful advanced/reference interfaces. A workspace keeps the files
separate while avoiding repeated filenames:

```yaml
workspace_version: "0.1"
input: ir-search-and-track.yaml
decisions: ir-search-and-track-decisions.yaml
mapping: ir-search-and-track-mapping.yaml
specific_functions: ir-search-and-track-specific-functions.yaml
profile: ../../profiles/oms/2.5/profile.yaml
```

```bash
python tools/completion.py worksheet examples/completion/ir-search-and-track-workspace.yaml
python tools/completion.py scaffold examples/completion/ir-search-and-track-workspace.yaml
```

The first reviews evidence; the second shows `MISSING` authoring fields. The
workspace does not merge these concepts together. It only saves the user from
repeatedly spelling out the filenames on every command. Consequently, this
intentionally incomplete real example fails closed at readiness:

```bash
python tools/completion.py check examples/completion/ir-search-and-track-workspace.yaml
```

After resolving authoring semantics, the complete synthetic exercise passes and
can emit the downstream artifact:

```bash
python tools/completion.py check examples/completion/complete-service-workspace.yaml
python tools/completion.py materialize examples/completion/complete-service-workspace.yaml \
  --format yaml --output contract.yaml
```

OMS-codegen consumes `contract.yaml` only, not the workspace, decisions,
mapping, structure, capabilities, or traceability artifacts. The following
sections explain each underlying file individually.

## Do I need the completion assistant?

The IR Search & Track snippets below teach the mechanics. For a full real-world
exercise showing why materialization can correctly remain blocked, see the
[RF FM Demod completion exercise](rf-fm-demod-completion-exercise.md).

The RF published-evidence example is incomplete and fail-closed. The companion
[RF FM Demod simulated owner-answer example](rf-fm-demod-owner-answer-loop.md)
uses the same evidence plus explicit labelled answers to materialize a valid
contract; it is illustrative, not an upstream contract.

There are three good workflows.

### I already know the contract

```text
I already know what my Service Contract should contain
        |
        v
write contract.yaml -> validate -> OMS-codegen
```

If you are designing a new service and already know its functions, exchanges,
topics, timing, mandate, and Capability structure, hand-authoring the portable
YAML is usually the simplest workflow. Validate it, then give it to OMS-codegen.

### I have incomplete source material

```text
documentation/configuration/code
        |
        v
record evidence -> review candidates -> make explicit decisions
        |
        v
declare structure -> inspect scaffold / missing fields
        |
        v
materialize contract -> validate -> OMS-codegen
```

The completion assistant is primarily an evidence-backed migration,
reconstruction, and authoring aid. It helps when sources contain useful facts but
no source is a complete machine-readable contract.

### I have source files and want transcription assistance

Write a hash-pinned, source-specific extraction recipe, then start at extract:

```bash
python tools/completion.py extract recipe.yaml --source-root local-checkout --format yaml
```

This optional stage produces the same unconfirmed completion input that can also
be hand-authored. Continue at `worksheet`; extraction never makes decisions or
portable semantics. See the [source extraction walkthrough](source-extraction-walkthrough.md).

## Mental model

Separate what a source says from what the author chooses:

```text
SOURCE MATERIAL
  OMS Service Contract / README / configuration / implementation
        |
        v
+----------------------+       +----------------------+
| Evidence candidates  | ----> | Author decisions     |
| "the source says..." |       | "we accept/choose..."|
+----------+-----------+       +----------+-----------+
           |                              |
           +--------------+---------------+
                          v
               +----------------------+
               | Structure + mapping  |
               | "where does it go?" |
               +----------+-----------+
                          v
               +----------------------+
               | Scaffold             |
               | known/profile/author |
               | /missing              |
               +----------+-----------+
                          v
                    Materializer
                          |
                          v
              portable contract.yaml -> OMS-codegen
```

Evidence candidates preserve observed facts and source locations. Author decisions
explicitly adopt a candidate or supply a design value. Structure says which
functions/exchanges exist; mapping says where a decision belongs. The scaffold is
a punch list, not a contract. Only successful materialization creates a portable
Service Contract.

This tutorial uses the checked-in IR Search & Track exercise. It is intentionally
incomplete: published evidence does not establish every semantic needed for a
final authored contract. That is useful teaching material.

## 1. Register sources and candidates

Open `examples/completion/ir-search-and-track.yaml`:

```yaml
sources:
  - id: primary-contract
    provenance: published_contract
    title: OMS Service Contract - IR Search and Track
    # uri and pinned revision omitted here
  - id: configuration-doc
    provenance: published_supporting_doc
    # title, uri, and revision omitted here
```

`primary-contract` is evidence. `configuration-doc` is evidence. Neither is
automatically copied into a portable Service Contract.

The same file records candidate facts:

```yaml
- id: position-direction
  target: exchange[PositionReport].direction
  value: input
  source: primary-contract
  locator: Section 4.2

- id: position-topic
  target: exchange[PositionReport].topic
  value: mission.position-report
  source: configuration-doc
  locator: position_topic
```

In plain English: the published contract says `PositionReport` is an input; the
configuration documentation says its topic is `mission.position-report`.

> A candidate is not contract semantics.

It means only: “we found this possible value in this source.” A target is an
opaque authoring label, not JSONPath and not an instruction to edit a contract.

## 2. Render the worksheet before decisions

```bash
python tools/completion_assistant.py \
  --input examples/completion/ir-search-and-track.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format markdown
```

Representative output:

```text
## Candidate evidence
exchange[PositionReport].direction | input | primary-contract | Section 4.2
exchange[PositionReport].topic     | mission.position-report | configuration-doc

## OMS profile requirements
Service Status — category: required; required group: service
  ServiceStatus: output, mandatory, periodic

## Remaining open decisions
- Confirm Capability inventory: unknown, explicitly zero, or declared.
- Review all candidate evidence before authoring contract semantics.

## Safety boundary
Candidate values are not Service Contract semantics until explicitly reviewed.
```

At this point you are not trying to produce YAML. Ask: what do sources say, do
they disagree, what OMS requirements apply independently, and what still needs a
human answer?

### Conflicts require an author

A hypothetical conflict is:

```yaml
- {id: status-topic-a, target: exchange[ServiceStatus].topic, value: status, source: source-a}
- {id: status-topic-b, target: exchange[ServiceStatus].topic, value: mission.service-status, source: source-b}
```

The worksheet retains both and reports conflicting candidate values: explicit
author decision required. The assistant never resolves conflicts by source
priority, declaration order, confidence score, or guessing.

## 3. Make decisions and map them

`examples/completion/ir-search-and-track-decisions.yaml` adopts exact evidence:

```yaml
- target: exchange[PositionReport].direction
  select_candidate: position-direction

- target: exchange[PositionReport].topic
  select_candidate: position-topic
```

`select_candidate` means: **the author explicitly adopts this exact evidence
record**. A decision can instead be an author-created value:

```yaml
- target: function[Service Status].id
  value: service-status
```

`value` means: **this did not come from source evidence**. The tooling keeps the
two cases distinguishable.

The worksheet target does not itself modify a contract. The mapping file provides
the typed destination:

```yaml
- target: exchange[ServiceStatus].topic
  destination:
    kind: required_exchange_field
    profile_function: Service Status
    selector: ServiceStatus
    field: topic
```

Read it as: use this decision; it belongs to an OMS-required exchange; the owner
is Service Status; the exchange is ServiceStatus; populate its topic.

```text
author decision: exchange[ServiceStatus].topic
                    |
                    v
typed mapping -> Service Status -> ServiceStatus -> topic
```

## 4. Structure is separate from values

`examples/completion/ir-search-and-track-specific-functions.yaml` says:

```yaml
# Authoring exercise only: published sources do not establish this grouping.
specific_functions_version: "0.1"
functions:
  - key: ir-authoring-exercise
    exchanges:
      - key: position-report
        kind: oms_message
      - key: observation-report
        kind: oms_message
```

This answers “what functions/exchanges exist and how are they grouped?” It does
not supply portable function ID/name, exchange ID/message, mandate, or timing.
The comment matters: grouping is an authoring decision, not an evidence inference.

## 5. Render the scaffold and resolve `MISSING`

```bash
python tools/completion_scaffold.py \
  --input examples/completion/ir-search-and-track.yaml \
  --decisions examples/completion/ir-search-and-track-decisions.yaml \
  --mapping examples/completion/ir-search-and-track-mapping.yaml \
  --specific-functions examples/completion/ir-search-and-track-specific-functions.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format markdown
```

The Markdown scaffold is the author’s punch list:

```text
# Completion authoring scaffold
- `functions[Service Initialization].id`
- `functions[Service Status].id`
- `functions[Service Status].exchanges[ServiceStatus].id`
- `functions[Service Status].exchanges[ServiceStatusDataRequest].topic`
- `functions[ir-authoring-exercise].applicability`
```

Those paths are `MISSING`. Use `--format json` for detailed typed scaffold states;
there profile-derived values, resolved decisions, and missing fields remain
separate. For every missing value, only a few paths are legitimate:

1. Find stronger source evidence.
2. Ask the service owner or system engineer.
3. Make an explicit design decision.
4. Mark a function/exchange not applicable where the model allows it.

Do not assume “the tool probably knows.” It intentionally does not.

## 6. What the OMS profile supplies

The profile supplies fixed OMS semantics, not local identity or deployment facts.

| Field | Source |
| --- | --- |
| Function name `Service Status` | OMS profile |
| Category `required` | OMS profile |
| Required group `service` | OMS profile |
| Exchange message `ServiceStatus` | OMS profile |
| Direction `output` | OMS profile |
| Mandate `mandatory` | OMS profile |
| Timing kind `periodic` | OMS profile |
| Function ID | Author |
| Exchange ID | Author |
| Topic | Author/evidence |
| Nominal rate | Author/evidence if supplied |

OMS requiring ServiceStatus does not prove that observed source documentation
completely satisfies Service Status.

## 7. Capabilities and traceability

Capabilities are explicit author declarations, never message-name inference:

```yaml
capabilities:
  - id: esm
    name: ESM
    requires_position_information: true
```

The OMS profile then derives Section 3.3 topology: ESM has
`capability_status`, `capability_enable_disable`, and `capability_operations`.
The component has one `position_information_processing` function. `SignalReport`
does not automatically mean ESM, and Position Information Processing is once per
component, not once per Capability.

Candidate provenance asks “where did we observe this possible value?” Portable
traceability asks “which adopted source does this final function/exchange cite?”
They are independent. For example, configuration evidence can supply a topic,
while a final exchange explicitly traces to a primary-contract section. See
[completion traceability](../completion-traceability.md) for the adoption and
attachment artifact.

## 8. Materialize a complete contract

IR Search & Track teaches incomplete evidence handling. The synthetic complete
exercise teaches successful materialization:

```bash
python tools/completion_materialize.py \
  --input examples/completion/complete-service.yaml \
  --decisions examples/completion/complete-service-decisions.yaml \
  --mapping examples/completion/complete-service-mapping.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format yaml \
  --output contract.yaml
```

It produces real portable YAML:

```yaml
contract_version: '0.1'
service:
  name: Synthetic Completion Service
  version: 1.0.0
  kind: service
standards:
  oms_version: '2.5'
functions:
- id: service-initialization
```

> This is now a portable Service Contract. The worksheet and scaffold were not.

Materialization validates portable `SC_*` and selected OMS-profile `OP_*` rules
before emitting bytes.

## 9. Validate and hand off

Validate the standalone artifact, including the selected profile:

```bash
python tools/validate.py --profile profiles/oms/2.5/profile.yaml contract.yaml
```

Then hand it to OMS-codegen:

```bash
ams-gra-codegen-oms service-plan \
  --contract contract.yaml \
  --schema /path/to/UCI_MessageDefinitions_v2_5_0.xsd
```

```text
contract.yaml -------------------+
                                 |
                                 v
                         Resolved Service Plan
                                 ^
                                 |
UCI XSD -> Schema IR ------------+
```

The Service Contract says which messages, directions, topics, function ownership,
and timing/mandate apply. UCI says what those messages contain. OMS-codegen joins
them. This repository does not invoke or depend on OMS-codegen.

## Quick recipe

### New service

1. Hand-write `contract.yaml`.
2. Validate it.
3. Feed it to OMS-codegen.

### Existing or incompletely documented service

1. Optionally extract candidates from verified local sources, or register them by hand.
2. Record/review candidate facts.
3. Render the worksheet.
4. Resolve conflicts.
5. Record author decisions.
6. Declare specific-function/Capability structure where needed.
7. Map decisions.
8. Render the scaffold.
9. Resolve every `MISSING` field.
10. Add explicit traceability if desired.
11. Materialize.
12. Validate.
13. Feed the contract to OMS-codegen.

## Common mistakes

- **Candidate exists, so the field is decided.** No: `candidate -> explicit author
  decision -> mapping -> contract`.
- **The assistant will infer functions.** No: `PositionReport` does not imply
  Position Information Processing.
- **Message names infer Capabilities.** No: `SignalReport` is not automatically
  an ESM Capability.
- **Profile requirements prove evidence satisfaction.** No: requirements do not
  prove source documentation completely satisfies them.
- **Completion is always necessary.** No: if the design is complete, hand-author
  portable YAML instead.

For detailed reference rules, see [completion assistant](../completion-assistant.md),
[completion scaffold](../completion-scaffold.md),
[completion capabilities](../completion-capabilities.md),
[completion specific functions](../completion-specific-functions.md), and
[completion materialization](../completion-materialization.md).
