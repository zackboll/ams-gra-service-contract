# Versioning Model

This project intentionally separates several version domains that are easy to conflate.

## 1. Contract-language version

Example:

```yaml
contract_version: "0.1"
```

This selects the syntax and semantics defined by this repository.

A parser/generator must support this version explicitly. It must not assume that a newer or older contract-language version is compatible.

Before 1.0, minor versions may contain breaking changes. After 1.0, the project intends to use semantic versioning principles for the contract language.

## 2. OMS version

Example:

```yaml
standards:
  oms_version: "2.5"
```

This identifies the OMS version/profile context used to interpret Service Contract expectations.

The JSON syntax schema deliberately does not embed an OMS 2.5 required-function catalog. A version-aware profile validator should enforce OMS-version-specific requirements.

## 3. UCI schema version

Example:

```yaml
standards:
  uci_schema_version: "2.5"
```

This selects the baseline UCI schema against which `oms_message.message` references must be resolved.

A toolchain should map the declared version to an exact schema artifact/digest, not merely search the filesystem for a similar filename.

## 4. UCI extension schemas

Extension schemas are independently declared:

```yaml
uci_extension_schemas:
  - program-extension-1.3
```

The generator/toolchain owns the mapping from this stable identifier to concrete schema files. Builds should record file digests for reproducibility.

## 5. AMS GRA version

Optional:

```yaml
standards:
  ams_gra_version: "..."
```

AMS GRA context is not inferred from OMS or UCI versions. A particular integration may intentionally combine explicitly compatible releases.

## 6. Service implementation version

Example:

```yaml
service:
  version: "3.4.1"
```

This identifies the software implementation described by the contract. It is independent of all architecture/specification versions.

## 7. Generator version

The code generator is outside this repository and should have its own release/version.

Generated output should ideally record a manifest similar to:

```text
contract language: 0.1
contract digest:   sha256:...
OMS:               2.5
UCI:               2.5
UCI schema digest: sha256:...
generator:         0.4.2 / commit ...
backend:           ada 0.3
```

## 8. Compatibility matrix

A generator should publish an explicit support matrix rather than guessing. Example shape:

| Generator | Contract language | OMS profile validation | UCI parser support |
|---|---|---|---|
| 0.4.x | 0.1 | 2.5 | 2.5, 2.6 |

The presence of two UCI versions in a parser does not mean an OMS profile is automatically compatible with both. Compatibility claims require explicit validation.

## 9. Source pinning

Examples/documentation may link to moving `main` branches for discoverability. Production build inputs should prefer:

1. immutable release artifact;
2. tag plus verified digest;
3. commit SHA;
4. moving branch only as a development convenience.
