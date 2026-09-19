# Validation diagnostics

The validation and schema-source tools report a stable symbolic code, a path,
and a human-readable message for every diagnostic. Codes let tests and
downstream tools identify a failure class without parsing English prose:

```text
SC_DUPLICATE_FUNCTION $.functions: duplicate function id 'foo'
OP_MISSING_REQUIRED_FUNCTION $.functions: OMS profile 'oms-2.5' requires function 'Service Status' for service
```

The code is the stable public identity, the path identifies the affected
location, and the message provides descriptive context. Message wording may
improve without changing the code. Codes classify a failure category; they do
not encode a particular function, message, path, or array index.

The published validation taxonomy is pre-1.0 but symbolic codes are intended to
remain more stable than prose once published. JSON-Schema failures are
deliberately coarse-grained rather than assigning a public code per schema
keyword.

## Portable Service Contract (`SC_*`)

| Code | Meaning |
| --- | --- |
| `SC_SCHEMA` | Contract JSON-Schema or input parsing failure. |
| `SC_DUPLICATE_SOURCE` | Duplicate contract source ID. |
| `SC_DUPLICATE_FUNCTION` | Duplicate contract function ID. |
| `SC_DUPLICATE_EXCHANGE` | Duplicate exchange ID within one function. |
| `SC_UNKNOWN_TRACE_SOURCE` | Function or exchange traceability refers to an unknown source. |

## OMS profile (`OP_*`)

| Code | Meaning |
| --- | --- |
| `OP_SCHEMA` | Profile JSON-Schema or input parsing failure. |
| `OP_DUPLICATE_SOURCE` | Duplicate profile source ID. |
| `OP_DUPLICATE_FUNCTION` | Duplicate canonical required-function name. |
| `OP_DUPLICATE_APPLIES_TO` | Duplicate component kind in `applies_to`. |
| `OP_UNKNOWN_TRACE_SOURCE` | Required-function or required-exchange traceability refers to an unknown source. |
| `OP_DUPLICATE_EXCHANGE_RULE` | Duplicate semantic required-exchange rule. |
| `OP_UNSUPPORTED_CONTRACT_VERSION` | Profile does not support the contract language version. |
| `OP_OMS_VERSION_MISMATCH` | Contract OMS version differs from the profile OMS version. |
| `OP_MISSING_REQUIRED_FUNCTION` | Required canonical function is absent. |
| `OP_AMBIGUOUS_REQUIRED_FUNCTION` | Multiple contract functions match one canonical required function. |
| `OP_FUNCTION_METADATA` | Required function category or required group is wrong. |
| `OP_FUNCTION_APPLICABILITY` | Required function fixed or allowed applicability is wrong. |
| `OP_MISSING_REQUIRED_EXCHANGE` | Required semantic exchange shape is absent. |

When contract-version or OMS-version compatibility fails, profile application
returns only those compatibility diagnostics. Ordinary contract structural
validation runs before profile application, so invalid portable documents yield
`SC_SCHEMA` rather than being masked by profile diagnostics.

## Schema source (`SS_*`)

`SS_*` means the failure is owned by schema-source manifest, composition, or
verification semantics. `compose_schema_source_set()` may return `SC_*`
diagnostics when its input contract is invalid. The path and message provide
context while the code identifies the category.

| Code | Meaning |
| --- | --- |
| `SS_SCHEMA` | Manifest JSON-Schema validation or manifest YAML/JSON parsing failure. |
| `SS_UNSAFE_PATH` | Root schema or manifest file path is not a canonical safe relative POSIX path. |
| `SS_DUPLICATE_FILE` | Manifest file paths are not unique. |
| `SS_FILE_ORDER` | Manifest file list is not lexicographically ordered. |
| `SS_ROOT_SCHEMA` | Root schema does not appear exactly once in `files`. |
| `SS_FILE_OUTSIDE_ROOT` | A resolved manifest file escapes the supplied source root. |
| `SS_FILE_MISSING` | A manifest-declared file does not exist locally. |
| `SS_FILE_READ` | A manifest-declared file could not be read. |
| `SS_HASH_MISMATCH` | Actual bytes do not match the manifest SHA-256. |
| `SS_SOURCE_ROOT_SET` | Supplied source-root IDs do not exactly match the selected schema-source set. |
| `SS_BASELINE_SELECTION` | Baseline manifest role, family, or version is incompatible with the contract. |
| `SS_EXTENSION_MAPPING` | Declared and supplied extension manifest IDs, roles, or families do not map exactly. |
| `SS_EXTENSION_COMPATIBILITY` | A selected extension is incompatible with the contract UCI baseline version. |
| `SS_MANIFEST_ID_COLLISION` | Colliding baseline or extension manifest IDs make composition ambiguous. |

Resolver and projection code families remain unpublished.
