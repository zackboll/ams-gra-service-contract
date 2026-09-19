# AMS GRA Machine-Readable Service Contract

> **Status:** experimental specification draft (`contract_version: "0.1"`). This repository is independent work. It is **not** an official AMS GRA, OMS, UCI, Open Architecture Management Office, or U.S. Government artifact, and it does not replace the official OMS Service Contract.

This repository defines a small, language-neutral, machine-readable representation of the **service interface information that is otherwise captured in an OMS Service Contract**. Its primary purpose is to make that information usable as an input to code generators, validators, test generators, deployment tooling, and documentation tooling. It also includes non-normative reference tooling needed to exercise the specification against real upstream material while keeping the portable format language-neutral.

The central design rule is:

> **UCI defines what an OMS message is. The machine-readable service contract defines which exchanges a particular service uses, in which direction, for which function, and with which Service Contract metadata.**

The format deliberately does **not** copy UCI message layouts or message primitive metadata. The included offline resolver is a non-normative Python reference implementation: it verifies selected external UCI schema bytes, indexes global declarations, and derives message QNames, UCI primitives, and exact global message type QNames for the message names declared by the contract. It identifies type declarations only; it does not model type contents or layouts, and its Python models are not a standardized generator API or portable resolved-contract IR.

## Schema-source manifests

`standards.uci_schema_version` identifies a logical UCI version, not exact
schema bytes. Toolchains can map it to a separately versioned schema-source
manifest that pins an immutable upstream revision, root XSD, required file set,
and SHA-256 digests. This manifest is not part of the portable Service Contract
grammar. See [docs/schema-sources.md](docs/schema-sources.md).

Toolchains compose one matching baseline manifest plus only the extension
manifests explicitly declared by the contract, failing when exact ID mapping or
baseline compatibility is incomplete.

## Inputs/Outputs projection

The non-normative reference tool `tools/io_projection.py` derives a deterministic
human-readable Markdown summary or JSON tooling output from a validated contract
and manifest-verified UCI bytes. It retains authored function/exchange order and
keeps ownership clear: the contract supplies use, direction, mandate, topic, and
timing; UCI supplies primitive and QName/type identity. It is not official OMS
Service Contract or DOCX generation. See
[docs/inputs-outputs-projection.md](docs/inputs-outputs-projection.md).

## Profile validation

The generic v0.1 schema is OMS-version-neutral. Opt-in profiles provide
version-specific conformance checks without coupling contract language version
to OMS version. For the initial OMS 2.5 required-service profile:

```bash
python tools/validate.py \
  --profile profiles/oms/2.5/profile.yaml \
  my-complete-service.yaml
```

For `service` and `isolator`, it requires the canonical functions **Service
Initialization** and **Service Status** with required/service/applicable
metadata, including their minimum exchange surfaces. For `subsystem`, it
requires the Section 3.2 inventory **Subsystem Startup**, **Subsystem Status**,
**Subsystem State Command Processing**, **Subsystem Built-In Test (BIT)**,
**Subsystem Calibration**, and **Subsystem Shutdown**. It also requires the
three minimum Subsystem Status OMS-message shapes: periodic `SubsystemStatus`
output, asynchronous `SubsystemStatusDataRequest` input, and on-demand
`SubsystemStatusDataRequestStatus` output. Matching is semantic and does not
fix local IDs, topics, operational attributes, numerical timing values, Appendix
C, or UCI primitives. Required inventory/section presence is distinct from
`applicability: applicable`: State Command Processing, BIT, and Calibration may
be explicitly `not_applicable` with the portable-contract rationale and empty
exchange requirements. Remaining Section 3.2 exchange gaps are Subsystem
Startup, State Command Processing, BIT, Calibration, and Shutdown. The profile
does not claim full OMS Subsystem compliance.
Normal `--all` validation remains profile-free because examples can be valid
source-backed function fragments rather than complete Service Contracts. See
[docs/profiles.md](docs/profiles.md).

## Why this repository exists

The upstream architecture already has two complementary kinds of information:

1. **UCI schema and interface material** defines the standardized message vocabulary and message structure.
2. **OMS Service Contracts** describe a particular Service's functions and the inputs/outputs associated with those functions.

Those sources are excellent for human integration and compliance work, but there is a tooling gap when building multiple strongly typed implementations. A language generator needs to know more than `ServiceStatus` exists; it needs to know whether *this Service* subscribes to it, publishes it, whether the exchange is mandatory or optional for a function, which topic/configuration is used, and the declared exchange timing category.

Without a shared machine-readable contract, those service-specific decisions tend to be repeated independently in:

- Ada/SPARK bindings and service interfaces;
- Rust traits and adapters;
- C++ interfaces;
- Python service glue;
- CAL/Sleet deployment configuration;
- test harnesses;
- integration documentation; and
- compliance/traceability evidence.

That duplication creates opportunities for drift. A publisher added in code may be missing from deployment authorization. A topic may be renamed in one language but not another. A generated interface may expose messages the Service Contract never declared. A test suite may verify a different surface than the integration documentation.

This repository is intended to provide a **single, reviewable, versioned source for that service-specific interface declaration**.

## Why a separate repository

This format is intentionally separate from any Ada, Rust, C++, Python, or Sleet implementation because no one implementation language should own the semantics of an architecture-level contract.

Keeping the specification separate provides:

- **language neutrality** — all code generators consume the same source;
- **independent versioning** — the contract language can evolve without forcing a release of every backend;
- **shared conformance fixtures** — all consumers can validate against the same valid/invalid examples;
- **clear ownership boundaries** — this repository specifies the interchange format, while generators own their internal IRs and emitted code;
- **reviewable architectural changes** — a Service's interface changes can be reviewed as data rather than inferred from implementation diffs; and
- **reusability** — documentation generators, deployment tools, linters, or future formal-analysis tools can consume the same contract without depending on a particular code generator.

A generator-specific **Contract IR** does *not* belong here. This repository defines the portable input format and its semantics. Each generator may lower it into its own internal representation.

## Relationship to upstream AMS GRA, OMS, and UCI

This project is a companion representation, not a replacement standard.

```text
             Upstream architecture / standards

      AMS GRA               OMS                 UCI
         |                   |                   |
         |          Service Contract rules      |
         |                   |             message schema
         |                   |                   |
         +-------------------+-------------------+
                             |
                             v
                   service-contract.yaml
                              |
                   structural validation
                              |
                              v
                        Contract Model
                              |
                              | contract.standards.uci_schema_version
                              v
                 toolchain schema-source selection
                              |
                              v
                     schema-source manifest
                              |
                    verify local UCI schema bytes
                              |
                              v
                  UCI XSD set --> UCI parser
                              |             |
                              +-- resolve --+
                                            |
                                            v
                                 Resolved Service IR
                             |
          +------------------+------------------+
          |          |        |        |         |
         Ada        Rust     C++     Python    tooling
        /SPARK                                  /docs
```

For AMS GRA context, begin with the public upstream architecture repository, especially:

- [AMS GRA repository](https://github.com/open-arsenal/ams-gra)
- [AMS GRA Service MPU architecture volume](https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/AMS_GRA_Service_MPU.pdf)
- [OMS Service MPU architecture volume](https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/OMS_Service_MPU.pdf)
- [Software Architecture volume](https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/Software_Architecture.pdf)
- [Mission Agnostic Service Infrastructure volume](https://github.com/open-arsenal/ams-gra/blob/main/Architecture_Volumes/Mission_Agnostic_Service_Infrastructure.pdf)

For the OMS Service Contract semantics represented here, the primary upstream sources are:

- [OMS repository](https://github.com/open-arsenal/oms)
- [OMS Standard v2.5, OMSC-STD-001 Rev M](https://github.com/open-arsenal/oms/blob/main/docs_official/02_OMSC-STD-001_RevM_OMS_Standard_DandD_v2_5.docx)
- [CAL Specification v2.5, OMSC-SPC-001 Rev L](https://github.com/open-arsenal/oms/blob/main/docs_official/04_OMSC-SPC-001_RevL_CAL_Specification_DandD_v2_5.docx)
- [Service Contract Template v2.5, OMSC-TMP-003 Rev M](https://github.com/open-arsenal/oms/blob/main/docs_official/14_1_OMSC-TMP-003_RevM_ServiceContractTemplate_DandD_v2_5.docx)
- [Service Contract Instructions v2.5, OMSC-INS-003 Rev M](https://github.com/open-arsenal/oms/blob/main/docs_official/14_2_OMSC-INS-003_RevM_ServiceContractInstructions_DandD_v2_5.docx)
- [Language-Agnostic CAL Specification v2.5, OMSC-SPC-013 Rev B](https://github.com/open-arsenal/oms/blob/main/docs_official/20_OMSC-SPC-013_RevB_LanguageAgnostic_CAL_Specification_DandD_v2_5.docx)

For message definitions, use the public upstream [UCI repository](https://github.com/open-arsenal/uci). The contract declares a logical `uci_schema_version`; a toolchain maps that version to a schema-source manifest, which pins the exact revision, file set, and digests.

See [docs/references.md](docs/references.md) for a fuller source map and status notes, and [docs/upstream-mapping.md](docs/upstream-mapping.md) for a field-by-field mapping to the OMS Service Contract concepts.

## What v0.1 represents

Version 0.1 focuses on the parts of the OMS Service Contract Inputs and Outputs table that are directly useful to generators and validators:

- Service identity and implementation version;
- OMS and UCI schema versions;
- function identity, category, applicability, and optional traceability;
- exchange direction (`input` or `output`);
- data-exchange kind:
  - OMS Message,
  - Data Transfer,
  - Special Signal,
  - Security Exchange,
  - Non-OMS Message;
- OMS message name and topic/configuration data;
- Level of Mandate (`mandatory` or `optional`);
- exchange timing category:
  - asynchronous,
  - on-demand,
  - periodic;
- informative nominal/max timing values where present; and
- traceability back to source artifacts.

The OMS Service Contract material treats Message Primitive as UCI-owned metadata. In the pinned public UCI 2.5 XSD it is serialized in `xs:documentation` as `UCI_PRIMITIVE: <value>.`; therefore **v0.1 intentionally does not store message primitive in the contract**.

The v0.1 `data_transfer` exchange models the Data Transfer information carried by a function Inputs/Outputs row. It does not yet attempt to model the complete Section 1.6 Data Transfer inventory.

## What v0.1 does not attempt

Version 0.1 is deliberately not a full executable specification of an OMS Service Contract. It does not yet formalize:

- arbitrary prose preconditions or postconditions;
- workflow/orchestration state machines;
- sequence diagrams;
- error-handling behavior;
- Service Level Agreements;
- security policy semantics beyond identifying a Security Exchange;
- complete Section 1.6 Data Transfer inventory semantics;
- MEL/MFA APIs;
- Skill composition;
- resource-management policy;
- complete regeneration of every section of the official Service Contract template; or
- a formal guarantee that an implementation conforms to AMS GRA, OMS, or UCI.

Those may be layered on later only when their semantics can be defined without inventing behavior that the upstream material does not specify.

## Quick start

Create a Python environment and install the development dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Run the complete repository validation suite (text hygiene, checked-in
schema-source manifest validation, contract/example validation, and pytest):

```bash
make check
```

Validate a specific contract:

```bash
python tools/validate.py examples/service-status.yaml
```

This performs **local contract validation only**. To resolve OMS Messages from verified local XSD bytes, use `python tools/uci_resolver.py resolve`; it never fetches external sources.

## Reference examples

The following are source-backed mappings of upstream OMS examples, not official
generated OMS Service Contracts:

- [`examples/service-status.yaml`](examples/service-status.yaml): Required
  Service Function / status example.
- [`examples/capability-enable-disable.yaml`](examples/capability-enable-disable.yaml):
  Required Capability-related Command / Command Status example.
- [`examples/service-initialization.yaml`](examples/service-initialization.yaml):
  Required Service Function containing both OMS Message and Data Transfer inputs.
- [`examples/subsystem-status.yaml`](examples/subsystem-status.yaml): Required
  Subsystem Function / status example.

## Minimal example

```yaml
contract_version: "0.1"

service:
  name: example-service
  version: "0.1.0"
  kind: service

standards:
  oms_version: "2.5"
  uci_schema_version: "2.5"

functions:
  - id: example-function
    name: Example Function
    category: specific
    applicability: applicable
    exchanges:
      - id: position-report-input
        kind: oms_message
        direction: input
        mandate: mandatory
        message: PositionReport
        topic: PositionReport
        timing:
          kind: asynchronous
```

`PositionReport` in this example is a reference into the selected UCI schema. A resolver should fail generation if that message cannot be resolved in the declared baseline UCI schema plus declared extension schemas.

## More complete Service Status example

The repository also includes [examples/service-status.yaml](examples/service-status.yaml), which demonstrates the shape needed to represent the OMS Service Status function, including periodic, asynchronous, and on-demand exchanges and source traceability.

The example preserves the upstream distinction between **contract metadata** and **message-schema metadata**:

```yaml
- id: service-status-output
  kind: oms_message
  direction: output
  mandate: mandatory
  message: ServiceStatus
  topic: ServiceStatus
  timing:
    kind: periodic
    nominal_rate_hz: 1.0
```

There is intentionally no field like:

```yaml
primitive: Data-1
```

because that is UCI-owned information.

## Validation model

A production consumer should validate a contract in three layers.

### 1. Structural validation

Validate YAML/JSON against `schema/v0.1/service-contract.schema.json`.

This catches errors such as:

- unsupported direction;
- unknown field names;
- invalid exchange-kind-specific fields;
- timing fields on the wrong timing kind; and
- malformed identifiers.

### 2. Contract semantic validation

Validate relationships not conveniently expressible in JSON Schema, including:

- duplicate source IDs;
- duplicate function IDs;
- duplicate exchange IDs within a function; and
- traceability references to unknown source IDs.

The included validator performs these checks.

### 3. UCI semantic resolution

A reproducible code generator or resolver should first map the logical
`uci_schema_version` to a selected schema-source manifest and verify the
manifest-declared external UCI schema bytes. It should then load that verified
schema set and verify:

- every `oms_message.message` exists;
- the message is resolved against the intended baseline/extension schema set;
- the UCI primitive is available from `UCI_PRIMITIVE:` documentation metadata;
- generated type information comes from UCI rather than the contract file; and
- ambiguities across extension schemas are diagnosed rather than guessed.

See [docs/code-generation.md](docs/code-generation.md).

The three layers above define contract validation and resolved-contract work;
external schema-source verification is a separate reproducibility check, not a
portable Service Contract conformance rule. In particular, contract conformance
is not external schema-source verification, and neither is resolved-contract
conformance.

## A proposed generator flow

```text
service-contract.yaml
        |
        v
structural + contract semantic validation
        |
        v
Contract Model ---- uci_schema_version --> toolchain schema-source selection
                                                |
                                                v
                                      schema-source manifest
                                                |
                                      verify local schema bytes
                                                |
                                                v
                                       UCI XSD set --> UCI Schema Model
                                                |             |
                                                +-- resolve --+
                                                              |
                                                              v
                                                   Resolved Service IR
                       |
          +------------+------------+
          |            |            |
          v            v            v
         Ada          Rust         C++      ...
        /SPARK
```

The **Resolved Service IR** is intentionally not standardized by this repository. It is an implementation detail of the consuming generator/toolchain.

## Code-generation policy guidance

A backend can use direction and message identity to generate a narrow interface instead of exposing a generic CAL surface.

For example, an Ada backend could emit conceptually:

```ada
procedure Handle_Service_Status_Data_Request
  (Request : UCI.Service_Status_Data_Request);

procedure Publish_Service_Status
  (Status : UCI.Service_Status);
```

A Rust backend could emit a trait with the corresponding typed handlers/publishers, and a C++ backend could generate an equivalent interface.

The important property is that **all backends start from the same contract declaration**.

The `mandate` field should not be casually reinterpreted as a language-level proof obligation. In OMS it describes whether an input/output is mandatory or optional to executing the function. A backend may choose to generate mandatory stubs or conformance checks, but that backend policy should remain explicit.

Similarly, the nominal and max response/rate values represented in v0.1 are **informative timing metadata**. They must not automatically become hard real-time deadlines, SPARK preconditions/postconditions, assertions, or schedulability claims.

## Sleet / LA-CAL configuration as a derived artifact

The AMS GRA Hello World Starter Kit's Sleet implementation demonstrates per-service topic/message authorization. That configuration is a good candidate for **derived output** from a resolved service contract:

```text
contract input/output declarations
            +
resolved UCI messages/topics
            |
            v
   deployment authorization
      (e.g. Sleet config)
```

The deployment configuration is not the Service Contract itself. It is one implementation/deployment artifact that can be generated from the contract.

## Repository layout

```text
.
├── README.md
├── INTENT.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE
├── Makefile
├── requirements-dev.txt
├── schema/
│   ├── v0.1/
│   │   └── service-contract.schema.json
│   ├── profile/
│   │   └── v0.1/
│   │       └── oms-profile.schema.json
│   └── schema-source/
│       └── v0.1/
│           └── schema-source-manifest.schema.json
├── schema-sources/
│   └── uci/2.5/
│       └── manifest.yaml
├── profiles/
│   └── oms/2.5/
│       └── profile.yaml
├── docs/
│   ├── specification.md
│   ├── rationale.md
│   ├── upstream-mapping.md
│   ├── code-generation.md
│   ├── versioning.md
│   ├── references.md
│   ├── profiles.md
│   ├── schema-sources.md
│   └── roadmap.md
├── examples/
│   ├── minimal.yaml
│   ├── service-status.yaml
│   ├── capability-enable-disable.yaml
│   └── service-initialization.yaml
├── tests/
│   ├── valid/
│   ├── invalid/
│   ├── profiles/
│   │   └── oms-2.5/
│   ├── test_validation.py
│   ├── test_text_hygiene.py
│   └── test_schema_sources.py
└── tools/
    ├── __init__.py
    ├── validate.py
    ├── check_text_hygiene.py
    └── schema_sources.py
```

## Normative vs. informative content in this repository

For this experimental specification:

- `schema/v0.1/service-contract.schema.json` is **normative for structure**.
- `docs/specification.md` is **normative for semantics**.
- conformance fixtures in `tests/` define expected validator behavior for the cases they cover.
- README, rationale, roadmap, examples, and code-generation guidance are **informative** unless explicitly stated otherwise.

If the JSON Schema and semantic specification disagree, that disagreement is a specification bug and should be reported rather than silently choosing one interpretation.

## Design principles

1. **Do not duplicate upstream truth.** UCI-owned facts stay in UCI.
2. **Be explicit about versions.** Contract-language, OMS, UCI, AMS GRA, and service versions are independent.
3. **Fail closed on ambiguity.** A resolver should report ambiguous/missing message references.
4. **Preserve upstream semantics.** Do not silently reinterpret Level of Mandate or informative timing columns.
5. **Keep the portable format language-neutral.** Ada/Rust/C++ details belong in backends.
6. **Make traceability first-class.** Architecture/specification source links can accompany functions and exchanges.
7. **Prefer a small stable core.** Add behavioral/formal semantics only when they are precisely defined.

## Versioning

The contract language begins at `0.1`. While the format is pre-1.0, breaking changes may occur between minor versions. A tool must reject a contract language version it does not understand rather than silently applying another version's rules.

OMS, UCI, AMS GRA, and Service implementation versions are independent and must never be inferred from `contract_version`.

See [docs/versioning.md](docs/versioning.md).

## Contributing

Semantic changes should include:

- a written rationale;
- an upstream source citation when the change claims to represent AMS GRA/OMS/UCI behavior;
- schema updates when structural changes are required;
- valid/invalid conformance fixtures; and
- documentation updates.

See [CONTRIBUTING.md](CONTRIBUTING.md).

For initial Git/GitHub publication steps, see [docs/bootstrap.md](docs/bootstrap.md).

## License and upstream rights

The source code and original specification text in this repository are licensed under Apache-2.0. Upstream AMS GRA, OMS, and UCI materials remain subject to their own notices, licenses, distribution statements, and terms. Links to upstream materials do not incorporate those documents into this repository or relicense them.

See [INTENT.md](INTENT.md) and [docs/references.md](docs/references.md).
