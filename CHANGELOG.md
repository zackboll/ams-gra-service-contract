# Changelog

All notable changes to this experimental specification and tooling project are documented here.

## [Unreleased]

### Added

- Opt-in OMS 2.5 Required Service Function profile validation.
- Automated repository text-hygiene enforcement.
- UCI 2.5 schema-source manifest with immutable source revision and SHA-256 verification.
- Deterministic schema-source set composition for one UCI baseline plus explicitly declared extension manifests, including exact extension-ID mapping, baseline compatibility checks, and contract-declaration ordering.
- Fail-closed message-resolution ambiguity semantics for future UCI XSD resolvers: zero candidates are unknown, one resolves, and multiple candidates are ambiguous.

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
