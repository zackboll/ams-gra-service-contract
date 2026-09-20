# Changelog

All notable changes to this experimental specification and tooling project are documented here.

## [Unreleased]

### Added

- RF FM Demod real published-service completion exercise with pinned evidence
  provenance, explicit profile-vs-evidence-vs-author distinction, concrete owner
  questions, and intentional fail-closed non-materialization. It records what is
  not demonstrated or requires author confirmation without a compliance verdict.

- Tooling-only completion workspaces and one `completion.py`
  worksheet/scaffold/check/materialize front door. References resolve relative
  to the workspace; this changes no portable v0.1 semantics or schema.

- Deterministic portable v0.1 YAML materialization and safe complete-contract
  `--output` emission. JSON remains the default; YAML/JSON serialize the same
  validated model. Existing files require explicit `--force` atomic replacement;
  this adds no semantic apply/edit behavior.

- Portable v0.1 machine-readable conformance pack with valid/invalid
  expectations, canonical schema fingerprint guard, and YAML/JSON equivalence
  cases. This locks the pre-1.0 compatibility surface without claiming 1.0
  format stability.

- Explicit tooling-only source adoption and function/exchange traceability
  authoring/materialization. Source keys remain local, evidence provenance and
  profile traceability are not copied automatically, and portable v0.1 grammar is
  unchanged.

- Explicit Capability completion artifacts, typed mappings, fail-closed
  materialization, and profile-derived OMS 2.5 Section 3.3 functions.

- Explicit tooling-only specific-function structural authoring, typed mapping,
  scaffold, and fail-closed materialization. Structure never infers grouping or
  portable IDs/names; Capability and standard-role inference remain absent.

- Fail-closed completion-scaffold materialization into deterministic portable
  Service Contract JSON. It refuses unresolved required values and unmapped
  author decisions, preserves lower-layer `SC_*`/`OP_*` validation diagnostics,
  has no file write/apply path, and omits unsupported capabilities, specific
  functions, and automatic provenance/traceability. A synthetic conformance
  exercise covers OMS Messages, Data Transfer, and all supported timing kinds.
- Typed completion-decision mappings and deterministic profile-derived authoring
  scaffold tooling. Bounded `CA_*` mapping diagnostics validate typed future
  destinations while preserving unmapped decisions and structural missing fields.
  No contract materialization, generated identity/topic/function, Capability
  scaffold, satisfaction analysis, or output/apply path is included.
- Optional explicit author-decision overlays for completion worksheets. Decisions
  separately select exact evidence candidates or supply scalar author values,
  retain evidence/provenance, and use stable decision-specific `CA_*`
  diagnostics. They do not generate, edit, map, or apply Service Contracts, and
  do not establish profile satisfaction. The IR Search and Track evidence pins
  the correct `sk-skills` repository URI and published configuration field names.
- Provenance-preserving, non-normative completion worksheet tooling with a
  standalone tooling schema, `CA_*` diagnostics, deterministic Markdown/JSON
  rendering, profile-derived fixed requirements, and the IR Search and Track
  evidence exercise. Candidates remain unconfirmed and conflicts are retained;
  no source extraction, inference, confirmation, core-schema change, or contract
  generation/apply path is included.
- Five-contract published OMS 2.5 evidence survey spanning RF FM Demod,
  Graupel, IR Search and Track, Supercell, and Squall OMS Adapters. It records
  pinned sources, provenance, profile and UCI resolver evidence, and selects an
  author-confirmed completion assistant as the next direction. No real-world
  YAML, schema/profile semantic change, Capability inference, or component-kind
  inference was added.
- Evidence-driven exercise of two published OMS 2.5 Service Contracts (RF FM
  Demod and Graupel), including field-level provenance/representability matrices,
  independent profile comparison, and real UCI 2.5 resolver results. Neither
  incomplete Markdown source was converted into invented YAML; schema and profile
  acceptance rules are unchanged. Regressions confirm omitted Capabilities are
  not inferred from RF message names and that Isolators never receive Section 3.3
  requirements from Capability-like terms.
- OMS 2.5 Section 3.3 Capability function inventory profile: additive optional
  `functions[].standard_role` supplies bounded role identity independent of
  display names and IDs. Explicit non-empty Capability inventories trigger three
  owned roles per Capability for Services/Subsystems and conditional one
  component-level Position Information Processing role. New stable
  `OP_MISSING_CAPABILITY_FUNCTION` and `OP_AMBIGUOUS_CAPABILITY_FUNCTION`
  diagnostics identify Capability IDs. No Section 3.3 exchange minimum or
  behavior rule is added.
- Optional portable Capability identity and ownership model: explicit
  `capabilities` declarations preserve omitted-versus-empty semantics; each
  Capability has an ID, display name, and explicit position-information Boolean;
  functions may reference a declared Capability ID. Deterministic `SC_*`
  diagnostics reject duplicate Capability IDs and unknown references. This is
  infrastructure only: no OMS Section 3.3 inventory, name heuristic, or profile
  enforcement is added.
- OMS 2.5 Capability Operations (Section 3.3.2.3/Table 3.3-4) OOXML exchange
  classification. `Entity`/`SignalReport` are removable green ESM examples and
  `ProductMetadata`/`ProductLocation`/`ImageFile` removable green PO/POST
  examples in every matcher-owned field; `ImageFile` Data Transfer metadata is
  green example content too. Generic Operations prose supplies no universal
  exchange shape; fixed Preconditions remain behavioral. No domain heuristic,
  profile rule, schema, validator, diagnostic, or public example was added.
- OMS 2.5 Capability Enable/Disable (Section 3.3.2.2/Table 3.3-3) OOXML
  exchange classification. `ESM_SettingsCommand` and
  `ESM_SettingsCommandStatus` are removable green examples in every
  matcher-owned field. Mixed generic prose fixes only Capability-relative
  command input, status output, and response behavior; it does not fix kind,
  mandate, or an OMS timing category. The public ESM example is clarified as an
  illustrative transcription, not a profile minimum. No ESM/literal-placeholder
  requirement, name heuristic, schema, validator, or diagnostic was added.
- OMS 2.5 Capability and Capability Status (Section 3.3.2.1/Table 3.3-2)
  OOXML exchange classification. `ESM_Capability` and
  `ESM_CapabilityStatus` are removable green examples in every matcher-owned
  field. Mixed generic prose establishes only Capability-relative output and
  periodic message-family behavior; it does not fix kind or mandate. Exact
  per-Capability validation remains deferred because v0.1 lacks explicit
  Capability identity and ownership. No ESM/literal-placeholder requirement,
  name heuristic, schema, validator, or diagnostic was added.
- OMS 2.5 Position Information Processing (Section 3.3.1/Table 3.3-1) OOXML
  exchange classification. `PositionReport` and `PositionReportDetailed` are
  green removable guidance in every matcher-owned table field, including LoM;
  black Description/Workflow prose establishes only a conceptual periodic input
  alternative, not machine-checkable cardinality or individual mandatory shapes.
  No universal Position Information function, exchange rule, schema, validator,
  diagnostic, or alternative DSL was added. Conditional Capability/function and
  possible alternative-exchange modeling remain deliberate future-design gaps.
- OMS 2.5 Required Capability-related Function (Section 3.3) OOXML inventory
  classification. The parent Capability-provider statement is fixed black, while
  Table 3.0-1 capability rows, applicability/N/A directions, Position
  Information conditionality, `[CapabilityName]` replacement, and copy-per-
  Capability directions are green template content. Exact per-Capability
  validation is deliberately deferred: v0.1 has no independent Capability
  identity/presence, ownership, or position-dependency model. No capability
  name heuristics, schema/profile rules, diagnostics, or exchange requirements
  were added.
- OMS 2.5 Subsystem Startup Table 3.2-1 and workflow OOXML source
  classification: `FileMetadata`, `FileLocation`, `Subsystem_OFP`,
  `SubsystemConfigFile`, and `MDF` have green removable guidance for every
  profile-matched field. The three MDF acquisition examples and their
  keep-one/remove-others instruction are green guidance, so Startup has no
  universal exchange minimum and no demonstrated fixed alternative-set modeling
  requirement. Optional LoM remains distinct from row presence; Example 3
  `QueryDataRequest`/`QueryDataRequestStatus` are not profile rules.
- OMS 2.5 Subsystem Calibration Table 3.2-5 OOXML source classification: all
  seven substantive rows have green removable guidance for every profile-matched
  field and green message-specific workflow prose, so Calibration has no
  exchange minimum. Optional LoM remains distinct from row presence; numeric
  timing is informative only; applicable and permitted N/A Calibration fixtures
  retain the existing conditional-applicability behavior.
- OMS 2.5 Subsystem Built-In Test (BIT) Table 3.2-4 OOXML source
  classification: all seven substantive rows are green removable guidance for
  every profile-matched field, so BIT has no exchange minimum. Optional LoM is
  kept distinct from row presence, and informative numeric timing is not
  profile-enforced.
- OMS 2.5 Subsystem State Command Processing Table 3.2-3 OOXML source
  classification and minimum command-input exchange validation:
  `SubsystemStateCommand` is OMS-message input, mandatory, and asynchronous.
  Both substantive rows are mixed, but every matched command field is fixed and
  fixed workflow prose corroborates receipt. The fixed table status-input versus
  workflow status-response conflict remains documented and is not
  profile-enforced.
- OMS 2.5 Subsystem Shutdown Table 3.2-6 OOXML source classification: the
  `SubsystemStateCommand`, `SubsystemStateCommandStatus`, and `Log_File` rows
  are all removable green guidance/example content, so no Shutdown exchange
  shape (including optional `Log_File`) is profile-enforced. The documented
  command-input/status-output guidance and 0.5/3-second timing remain
  informative only.
- Stable symbolic `IP_*` diagnostics for fail-closed Inputs/Outputs projection
  joins, while preserving lower-layer `SC_*`, `SS_*`, and `UR_*` identities
  through projection orchestration.
- Stable symbolic `UR_*` diagnostics for UCI resolver parsing and resolution,
  while preserving `SC_*` contract and `SS_*` schema-source diagnostic
  ownership through resolver orchestration.
- Stable symbolic `SS_*` diagnostics for schema-source manifest validation,
  composition, and local byte verification, preserving `SC_*` contract
  diagnostics during composition.
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
