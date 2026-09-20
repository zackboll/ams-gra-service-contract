# Portable Service Contract v0.1 conformance pack

This is a self-contained, machine-readable compatibility corpus for the portable
v0.1 contract surface. It is not an OMS profile, UCI resolver, completion tool,
or code generator test suite.

An independent implementation (including the first intended consumer,
[`ams-gra-codegen-oms`](https://github.com/zackboll/ams-gra-codegen-oms)) should:

1. read `manifest.json` and verify `contract_version` is supported;
2. verify the canonical schema fingerprint using the documented algorithm;
3. parse every case with its own YAML/JSON loader and validate it;
4. accept every `expect: valid` case and reject every `expect: invalid` case;
5. compare YAML/JSON cases in each `equivalence_group` as equal parsed models.

Reference diagnostic codes are optional metadata. Implementations need not use
Python exception wording, diagnostic codes, or paths. `SC_*` codes describe the
reference validator only.

The fingerprint is an accidental-change guard, not proof of semantic
compatibility. It is SHA-256 of UTF-8 canonical JSON: sorted keys, compact
`,`/`:` separators, and `ensure_ascii=False`; raw schema bytes are not hashed.

YAML duplicate keys are rejected as an input-format safety property before
portable semantic validation (`invalid/duplicate-yaml-key.yaml`). The corpus does
not require another implementation to report `SC_SCHEMA` for that condition.

Portable validity deliberately does not resolve UCI message selectors or
extension IDs. For example, `DoesNotExistInUCI` and `private-extension-1` can be
syntactically portable-valid; existence belongs to UCI/schema-source composition
or downstream code generation.
