# Versioning Model

This project intentionally separates several independently versioned domains
that are easy to conflate: contract version, profile version, manifest version,
OMS version, UCI version, service version, and generator version.

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

XSD namespace/message parsing remains future work. Until a resolver implements
it, toolchains must not infer message resolution or precedence from extension
ordering.

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

The code generator is outside this repository and should have its own release/version.

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

## 11. Source pinning

Examples/documentation may link to moving `main` branches for discoverability. Production build inputs should prefer:

1. immutable release artifact;
2. tag plus verified digest;
3. commit SHA;
4. moving branch only as a development convenience.
