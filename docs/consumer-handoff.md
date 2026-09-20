# Consumer handoff

This document defines the small, public surface for independent consumers such
as `ams-gra-codegen-oms`. `contract.yaml` is the boundary between authoring and
downstream generation:

```text
completion/source tooling -> contract.yaml <- UCI XSD
                                      |
                                      +-> downstream consumer
```

Completion tooling is optional. A valid hand-authored `contract.yaml` is a
first-class input. Consumers of portable contracts need only:

- `schema/v0.1/service-contract.schema.json`;
- `conformance/v0.1/` and its `manifest.json`;
- [versioning](versioning.md); and
- [portable conformance](portable-v01-conformance.md).

They do not need completion worksheets, decisions, mappings, extraction recipes,
workspaces, or profile-evidence artifacts unless they deliberately implement
authoring assistance.

## Independent implementation requirements

1. Support `contract_version: "0.1"` explicitly.
2. Consume `conformance/v0.1/manifest.json`.
3. Accept every valid case and reject every invalid case.
4. Preserve YAML/JSON equivalence semantics.
5. Do not depend on Python `SC_*` diagnostic wording.
6. Fail closed for unknown future fields or versions.

Verify the canonical schema fingerprint
`427fc250909ec40d82d1adc2daf236be2afe78a14f2b6ec80355b0105fe9e2e0`; this is
canonical JSON semantics, not a raw file digest.

## OMS profile boundary

OMS profile validation is an additional layer. A consumer can parse portable
`0.1` without implementing it. If implemented, `oms_version: "2.5"` maps to
`profiles/oms/2.5/profile.yaml`; it is never inferred from contract language.
UCI 2.6 resolver evidence does not establish an OMS 2.6 Service Contract profile.

## Code-generation handoff

The Service Contract owns service/function/exchange intent. UCI owns
message/type structure. Code generation joins contract-selected messages with a
normalized Schema IR. This does not prescribe generator internals or make the
reference Python resolver a generator API.

Recommended smoke fixtures are the existing conformance cases: `valid/minimal`,
`valid/all-exchanges-traceability`, `valid/capability-inventory`, and
`valid/materialized-complete-service`, plus invalid unsupported-version,
duplicate-function-ID, unknown-capability-reference, and unknown-traceability-
source cases. The RF FM Demod simulated-owner-confirmed expected YAML is a valid,
real-shaped, partially source-backed and partially simulated-owner-intent example;
it is not an official upstream RF FM Demod contract.
