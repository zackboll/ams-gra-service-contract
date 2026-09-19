# Changelog

All notable changes to this experimental specification and tooling project are documented here.

## [Unreleased]

### Added

- UCI 2.6 schema-source baseline with pinned extracted-XSD hashes, plus real
  UCI 2.5 -> 2.6 resolver regression evidence and continuity checks for
  repository-used message names.
- Stable symbolic `SC_*` and `OP_*` diagnostics for portable-contract and OMS
  profile validation, with code-first CLI rendering and public inventory.
- OMS 2.5 minimum Subsystem Status exchange-shape validation: periodic
  `SubsystemStatus` output, asynchronous `SubsystemStatusDataRequest` input,
  and on-demand `SubsystemStatusDataRequestStatus` output. Other Section 3.2
  exchange surfaces remain out of scope.
- OMS 2.5 Required Subsystem Function inventory validation, including explicit
  conditional applicability for State Command Processing, BIT, and Calibration;
  other Section 3.2 exchange inventories remain out of scope.
- Deterministic non-normative Inputs/Outputs Markdown and JSON projection
  tooling, joining contract-owned fields with manifest-verified UCI message
  primitive/QName/type identity without changing the portable grammar.
- Shared YAML 1.2-compatible, JSON-compatible input loading with duplicate-key rejection for contracts, profiles, and schema-source manifests.
- Explicit project boundary for non-normative reference validator/resolver tooling and intentionally limited UCI declaration resolution.
- Opt-in OMS 2.5 Required Service Function profile validation.
- OMS 2.5 minimum Service Status exchange-shape validation for Services and
  Isolators, with profile-source traceability and duplicate-rule checks.
- OMS 2.5 minimum Service Initialization exchange-shape validation for Services
  and Isolators: `FileMetadata`, `FileLocation`, and `ServiceConfigFile`.
- Discriminated OMS-profile required-exchange rules for OMS Messages and Data
  Transfers, with kind-specific duplicate detection and matching.
- Automated repository text-hygiene enforcement.
- UCI 2.5 schema-source manifest with immutable source revision and SHA-256 verification.
- Deterministic schema-source set composition for one UCI baseline plus explicitly declared extension manifests, including exact extension-ID mapping, baseline compatibility checks, and contract-declaration ordering.
- Offline UCI message resolution against verified schema-source bytes, including expanded-name identity, fail-closed ambiguity detection, and primitive extraction from public UCI XSD metadata.
- Immutable verified schema-source snapshots: XSD parsing consumes the exact single-read bytes whose SHA-256 digests were checked.
- Fail-closed message-resolution ambiguity semantics: zero candidates are unknown, one resolves, and multiple candidates are ambiguous.
- Namespace-aware global UCI type declaration indexing and fail-closed resolution of each primitive-tagged message's XSD `type` QName to exactly one global declaration. Type contents/layouts remain unmodeled.

## [0.1.0] - 2026-09-18

### Added

- Initial machine-readable Service Contract draft.
- JSON Schema Draft 2020-12 structural schema.
- Explicit Service, OMS, UCI, and optional AMS GRA version fields.
- Function category/applicability model.
- OMS Message, Data Transfer, Special Signal, Security Exchange, and Non-OMS Message types.
- I/O direction, Level of Mandate, and timing categories.
- Informative nominal/max timing metadata.
- Source traceability registry/references.
- Local semantic validator and conformance tests.
- Detailed rationale, code-generation architecture, versioning, references, and roadmap documentation.
