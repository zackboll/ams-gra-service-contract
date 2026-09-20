# Versioning Model

This project intentionally separates several independently versioned domains
that are easy to conflate: contract version, profile version, manifest version,
OMS version, UCI version, service version, and generator version.

## Repository/tooling release version

A Git tag such as `v0.2.0` versions this repository's schemas, reference
tooling, profiles, conformance pack, examples, and documentation as a bundle.
It does **not** imply `contract_version: "0.2"`. The prospective repository/
tooling release is `0.2.0`; the portable contract language remains `0.1`.

Release metadata is repository tooling, not portable Service Contract syntax.
The support manifest records the compatibility bundle. Consumers should prefer a
release tag plus its support manifest; during active development they should pin
an exact commit SHA rather than mutable `main`. The support manifest promises
repository-local compatibility surfaces that `release_check.py` validates offline;
it does not assert that every external evidence operation was re-executed.

For example, UCI schema-source baselines 2.5 and 2.6 are local manifest metadata.
The real cross-version resolver regression separately parses pinned UCI source
bytes with `tools/uci_version_regression.py`; it is not replayed by the release
checker.

## 1. Contract-language version

Example:

```yaml
contract_version: "0.1"
```

This selects the syntax and semantics defined by this repository.

A parser/generator must support this version explicitly. It must not assume that a newer or older contract-language version is compatible.

Before 1.0, minor versions may contain breaking changes. After 1.0, the project intends to use semantic versioning principles for the contract language.

## 2. Profile version

Example:

```yaml
profile_version: "0.1"
```

This versions an opt-in profile format independently of the contract language,
schema-source manifest format, and OMS version that a profile may target.

## 3. OMS version

Example:

```yaml
standards:
  oms_version: "2.5"
```

This identifies the OMS version/profile context used to interpret Service Contract expectations.

The JSON syntax schema deliberately does not embed an OMS 2.5 required-function catalog. A version-aware profile validator should enforce OMS-version-specific requirements.

## 4. UCI schema version

Example:

```yaml
standards:
  uci_schema_version: "2.5"
```

This identifies the logical baseline UCI release against which
`oms_message.message` references must be resolved.

A toolchain maps that logical version to an explicitly selected schema-source
manifest. The manifest then pins the exact upstream revision, root schema, file
set, and hashes; tools must not merely search the filesystem for a similar
filename.

## 5. Schema-source manifest version

Example:

```yaml
manifest_version: "0.1"
```

This versions the schema-source manifest format independently of the portable
contract language and any OMS profile. A manifest identifies exact external
schema-source bytes for a toolchain; it is not a field in the portable Service
Contract.

## 6. UCI extension schemas

Extension schemas are independently declared:

```yaml
uci_extension_schemas:
  - program-extension-1.3
```

The generator/toolchain maps this stable identifier by exact, case-sensitive
equality to a supplied extension schema-source manifest `id`. Each extension
manifest declares its own `schema_version` and the baseline versions it supports
through `compatible_baseline_versions`; it does not pretend its own version is
the UCI baseline version. Contract declaration order gives deterministic schema
set composition order, not implicit override precedence.

The reference resolver already performs namespace-aware message declaration and
primitive resolution and resolves each primitive-tagged message to its exact
global type declaration identity. It still does not infer override precedence:
zero, one, and multiple matching declarations remain unknown, resolved, and
ambiguous respectively.

## 7. AMS GRA version

Optional:

```yaml
standards:
  ams_gra_version: "..."
```

AMS GRA context is not inferred from OMS or UCI versions. A particular integration may intentionally combine explicitly compatible releases.

## 8. Service implementation version

Example:

```yaml
service:
  version: "3.4.1"
```

This identifies the software implementation described by the contract. It is independent of all architecture/specification versions.

## 9. Generator version

Language-specific code generators are outside this repository and should have
their own release/version. The repository's reference resolver is non-normative
tooling, not a generator backend or standardized generator IR.

Generated output should ideally record a manifest similar to:

```text
contract language:      0.1
contract digest:        sha256:...
OMS version:            2.5
OMS profile:            oms-2.5 / format 0.1
UCI logical version:    2.5
schema-source manifest: uci-2.5-baseline / format 0.1
manifest digest:        sha256:...
UCI revision:           093610...
generator:              0.4.2 / commit ...
backend:                ada 0.3
```

This example does not prescribe a generated-manifest serialization format.

## 10. Compatibility matrix

A generator should publish an explicit support matrix rather than guessing. Example shape:

| Generator | Contract language | OMS profiles | UCI parser support |
|---|---|---|---|
| 0.4.x | 0.1 | oms-2.5 | 2.5, 2.6 |

Profile support, UCI parser support, and OMS-version compatibility are separate
claims. Supporting UCI 2.6 does not mean the `oms-2.5` profile applies to OMS
2.6; compatibility claims require explicit validation.

## 11. Canonical schema fingerprint and source pinning

The canonical portable-schema fingerprint is a semantic compatibility guard: it
parses JSON, sorts keys, uses compact separators and `ensure_ascii=False`, then
SHA-256 hashes UTF-8 bytes. For portable `0.1` it is
`427fc250909ec40d82d1adc2daf236be2afe78a14f2b6ec80355b0105fe9e2e0`.
It is not a raw file SHA-256, which would change for whitespace-only edits.

Examples/documentation may link to moving `main` branches for discoverability. Production build inputs should prefer:

1. immutable release artifact;
2. tag plus verified digest;
3. commit SHA;
4. moving branch only as a development convenience.
