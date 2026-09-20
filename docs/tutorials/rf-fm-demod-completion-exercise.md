# RF FM Demod completion exercise

This real-world exercise shows why completion assistance is safer than opening a
blank Service Contract YAML file. RF FM Demod has useful published facts but not
the author-confirmed topology and local identifiers required to materialize a
portable contract.

## 1. Inspect pinned evidence

All evidence is pinned at RF FM Demod revision
`af13bd2926b15253e795920c91320733a29927ea`, not upstream `main`:

- [primary Service Contract](https://github.com/open-arsenal/ams-gra-hello-world-sk-skills-rf-fm-demod/blob/af13bd2926b15253e795920c91320733a29927ea/docs/compliance/oms-service-contract.md)
- [configuration](https://github.com/open-arsenal/ams-gra-hello-world-sk-skills-rf-fm-demod/blob/af13bd2926b15253e795920c91320733a29927ea/docs/configuration.md)
- [external interface contracts](https://github.com/open-arsenal/ams-gra-hello-world-sk-skills-rf-fm-demod/blob/af13bd2926b15253e795920c91320733a29927ea/docs/contracts.md)

Sections 1--3 establish RF FM Demod, version 1.0.0, OMS/UCI 2.5, AMS GRA
2026.01, and portable kind `service`. `Data Processor` is descriptive class
information, not a new portable kind. Sections 4.2--4.3 establish PositionReport
input, and ServiceStatus and SignalReport outputs; ServiceStatus is periodic.

Configuration supplies topic candidates and 1.0 Hz ServiceStatus rate. It also
observes a SignalReport 2.0 Hz implementation rate limit. The latter is retained
as `observation[SignalReport].report_rate_limit_hz`, not portable timing.
Similarly, threshold-trigger prose is not silently classified asynchronous, and
`capability_ids: []` is not portable `capabilities: []`.

`contracts.md` corroborates the three message directions and periodic ServiceStatus
behavior. It also describes command-line/configuration paths, JSON, environment
variables, RF MEL/MEL IQ interfaces, raw PCM TCP output, logs, and test fixtures.
Those are not added as OMS exchanges: this assistant constructs an OMS Service
Contract, not an inventory of every software interface.

## 2. Review the completion files

`examples/completion/rf-fm-demod.yaml` records 23 candidates and their source
locators. Matching facts from different source/provenance records are retained.
`rf-fm-demod-decisions.yaml` explicitly adopts identity/context values plus the
supporting ServiceStatus topic and nominal rate. `rf-fm-demod-mapping.yaml` maps
only those safe values. No Specific Function or Capability artifact exists because
the evidence establishes neither structure.

The workspace is the Task 045 front door:

```bash
python tools/completion.py worksheet examples/completion/rf-fm-demod-workspace.yaml
```

Representative actual output includes both provenance classes and the open
Capability question:

```text
| exchange[ServiceStatus].timing.kind | periodic | published_contract |
| exchange[ServiceStatus].timing.kind | periodic | published_supporting_doc |
- Confirm Capability inventory: Capability facts not supplied / unknown; ...
```

## 3. Read profile contribution and scaffold

OMS 2.5 independently supplies Service Initialization and Service Status topology.
For Service Status, it fixes the function/category/group/applicability and fixed
ServiceStatus, ServiceStatusDataRequest, and ServiceStatusDataRequestStatus kind,
selector, direction, mandate, and timing kind. Missing service-specific LoM is
therefore not a request to invent ServiceStatus mandate: the profile supplies
mandatory.

```bash
python tools/completion.py scaffold examples/completion/rf-fm-demod-workspace.yaml
```

Actual abbreviated `MISSING` output is:

```text
- `functions[Service Initialization].id`
- `functions[Service Initialization].exchanges[FileMetadata].topic`
- `functions[Service Initialization].exchanges[ServiceConfigFile].protocol`
- `functions[Service Status].id`
- `functions[Service Status].exchanges[ServiceStatus].id`
- `functions[Service Status].exchanges[ServiceStatusDataRequest].topic`
```

The full scaffold has 16 missing local fields: Service Initialization ID,
FileMetadata/FileLocation IDs and topics, ServiceConfigFile ID and transfer
metadata; and Service Status ID, ServiceStatus ID, and request/status IDs/topics.
Profile-owned direction, mandate, and timing do not appear missing. PositionReport
and SignalReport do not appear because their function ownership is intentionally
unconfirmed, not inferred.

Translate these fields into the concrete owner questions in
[RF FM Demod author questions](../examples/rf-fm-demod-author-questions.md).

## 4. Fail closed until the owner answers

```bash
python tools/completion.py check examples/completion/rf-fm-demod-workspace.yaml
```

Actual result (exit 1, no traceback):

```text
FAIL CA_MATERIALIZATION_INCOMPLETE unresolved required fields:
functions[Service Initialization].id,
... functions[Service Status].exchanges[ServiceStatus].id,
functions[Service Status].id
```

Materialization correctly refuses a partial contract:

```bash
python tools/completion.py materialize examples/completion/rf-fm-demod-workspace.yaml --format yaml
```

It exits 1 with the same diagnostic and empty stdout. With `--output`, it also
leaves no file. There is deliberately no RF FM Demod portable contract YAML.

## Why not blank YAML?

```text
Blank YAML: read docs -> fill obvious fields -> guess while editing -> lose the
distinction between evidence, OMS requirements, and author decisions.

Completion: source evidence + provenance -> explicit decisions -> OMS profile
fixed semantics -> scaffolded missing fields -> owner questions -> materialize
only when complete.
```

| Contract concept | Published evidence | OMS profile | Author still needed |
| --- | --- | --- | --- |
| Service name/kind/UCI version | RF FM Demod/service/2.5 | — | adopt candidates |
| ServiceStatus direction | output | output | no |
| ServiceStatus mandate/timing | periodic only | mandatory/periodic | no |
| ServiceStatus topic/rate | supporting candidates | — | selected here |
| ServiceStatus IDs | not stated | — | yes |
| PositionReport owner/mandate/timing | input | — | yes |
| SignalReport trigger/rate limit | threshold / 2.0 Hz observation | — | classify only if owner confirms |
| Capability inventory | not established | — | yes |

The next real-world step is not to guess: obtain the answers above, record them
as explicit decisions and structure, then rerun scaffold, check, and materialize.
