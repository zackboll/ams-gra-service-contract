# Diagnostics

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

## Ownership chain

| Family | Owner |
| --- | --- |
| `SC_*` | Service Contract |
| `OP_*` | OMS profile |
| `SS_*` | Schema-source selection and verification |
| `UR_*` | UCI parsing and resolution |
| `IP_*` | Inputs/Outputs projection join |
| `CA_*` | Completion assistant tooling workspace |
| `CF_*` | Portable conformance-pack tooling |

A higher-level tool can surface a lower-layer code unchanged; it does not take
ownership merely by orchestrating that layer.

Completion authoring owns `CA_*`; materialized portable semantics retain `SC_*`.
Workspace manifest parsing, path resolution, and command-stage requirements use
`CA_WORKSPACE_SCHEMA`, `CA_WORKSPACE_PATH`, and
`CA_WORKSPACE_STAGE_REQUIREMENT`. Workspace orchestration never relabels bad
completion artifacts (`CA_*`), portable contracts (`SC_*`), or OMS profiles
(`OP_*`).
Task 041 adds `CA_TRACEABILITY_SCHEMA`, `CA_DUPLICATE_SOURCE_KEY`,
`CA_UNKNOWN_EVIDENCE_SOURCE`, `CA_SOURCE_REVISION_MISMATCH`,
`CA_UNKNOWN_TRACE_SOURCE`, `CA_UNKNOWN_TRACE_TARGET`,
`CA_INACTIVE_TRACE_TARGET`, and `CA_DUPLICATE_TRACEABILITY`.

Extraction adds `CA_EXTRACTION_SCHEMA`, `CA_EXTRACTION_DUPLICATE_SOURCE`,
`CA_EXTRACTION_DUPLICATE_RULE`, `CA_EXTRACTION_UNKNOWN_SOURCE`,
`CA_EXTRACTION_PATH`, `CA_EXTRACTION_HASH`, `CA_EXTRACTION_MATCH`,
`CA_EXTRACTION_VALUE`, `CA_EXTRACTION_POINTER`, and
`CA_EXTRACTION_SERIALIZATION`. They identify recipe, verified-local-byte, exact
selector, scalar, or output-round-trip failures; no completion document is emitted.

Profile-evidence links add `CA_PROFILE_EVIDENCE_SCHEMA`,
`CA_PROFILE_EVIDENCE_DUPLICATE_TARGET`, `CA_PROFILE_EVIDENCE_DUPLICATE_FACT`,
`CA_PROFILE_EVIDENCE_UNKNOWN_TARGET`, `CA_PROFILE_EVIDENCE_UNKNOWN_FUNCTION`,
`CA_PROFILE_EVIDENCE_UNKNOWN_EXCHANGE`, `CA_PROFILE_EVIDENCE_FIELD`, and
`CA_PROFILE_EVIDENCE_NONFIXED`. Evidence disagreement is report data, not a diagnostic.

## Portable conformance pack (`CF_*`)

`CF_*` diagnoses the conformance manifest or corpus rather than a portable
contract. It is intentionally separate from `SC_*`: independent consumers must
make the valid/invalid acceptance decision, but do not need to reproduce the
Python reference validator's diagnostic wording or codes.

| Code | Meaning |
| --- | --- |
| `CF_SCHEMA` | Manifest parsing or tooling-schema validation failure. |
| `CF_DUPLICATE_CASE` | Case IDs or paths are not unique. |
| `CF_CASE_PATH` | A case path is unsafe, escapes the pack, or has no file. |
| `CF_SCHEMA_FINGERPRINT` | Canonical portable-schema SHA-256 differs from the manifest. |
| `CF_EXPECTATION` | A reference acceptance result differs from the declared case expectation. |
| `CF_REFERENCE_DIAGNOSTIC` | Declared reference `SC_*` identities differ from the reference result. |
| `CF_EQUIVALENCE` | A YAML/JSON equivalence group is malformed or not semantically equal. |

## Portable Service Contract (`SC_*`)

| Code | Meaning |
| --- | --- |
| `SC_SCHEMA` | Contract JSON-Schema or input parsing failure. |
| `SC_DUPLICATE_SOURCE` | Duplicate contract source ID. |
| `SC_DUPLICATE_CAPABILITY` | Duplicate contract Capability ID. |
| `SC_DUPLICATE_FUNCTION` | Duplicate contract function ID. |
| `SC_DUPLICATE_EXCHANGE` | Duplicate exchange ID within one function. |
| `SC_UNKNOWN_CAPABILITY` | Function Capability reference refers to an undeclared Capability. |
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
| `OP_MISSING_CAPABILITY_FUNCTION` | Required Capability role is absent; the message identifies its Capability ID when the role is per-Capability. |
| `OP_AMBIGUOUS_CAPABILITY_FUNCTION` | Multiple contract functions match one required Capability role; the message identifies its Capability ID when applicable. |
| `OP_FUNCTION_METADATA` | Required function category or required group is wrong. |
| `OP_FUNCTION_APPLICABILITY` | Required function fixed or allowed applicability is wrong. |
| `OP_MISSING_REQUIRED_EXCHANGE` | Required semantic exchange shape is absent. |

When contract-version or OMS-version compatibility fails, profile application
returns only those compatibility diagnostics. Ordinary contract structural
validation runs before profile application, so invalid portable documents yield
`SC_SCHEMA` rather than being masked by profile diagnostics.

## Completion assistant (`CA_*`)

| Code | Meaning |
| --- | --- |
| `CA_SCHEMA` | Completion-input JSON-Schema or input parsing failure. |
| `CA_DUPLICATE_SOURCE` | Duplicate completion source ID. |
| `CA_DUPLICATE_CANDIDATE` | Duplicate completion candidate ID. |
| `CA_UNKNOWN_SOURCE` | Candidate refers to an unknown completion source ID. |
| `CA_UNSUPPORTED_CONTRACT_VERSION` | Selected profile does not support the target contract version. |
| `CA_OMS_VERSION_MISMATCH` | Target OMS version differs from the selected profile OMS version. |
| `CA_DECISION_SCHEMA` | Completion-decisions JSON-Schema or input parsing failure. |
| `CA_DUPLICATE_DECISION_TARGET` | More than one author decision names the same worksheet target. |
| `CA_UNKNOWN_CANDIDATE` | A decision selects a candidate ID not present in the completion input. |
| `CA_DECISION_TARGET_MISMATCH` | A decision target differs from its selected candidate target. |
| `CA_MAPPING_SCHEMA` | Completion mapping schema or input parsing failure. |
| `CA_SPECIFIC_SCHEMA` | Specific-function structure schema or input parsing failure. |
| `CA_DUPLICATE_SPECIFIC_FUNCTION` | Specific-function structure repeats a function key. |
| `CA_DUPLICATE_SPECIFIC_EXCHANGE` | One specific function repeats an exchange key. |
| `CA_DUPLICATE_MAPPING_TARGET` | More than one binding uses a completion target. |
| `CA_DUPLICATE_MAPPING_DESTINATION` | More than one binding names a typed destination. |
| `CA_UNKNOWN_MAPPING_TARGET` | A mapping target is absent from candidates and decisions. |
| `CA_UNKNOWN_PROFILE_FUNCTION` | A mapping names no uniquely applicable profile required function. |
| `CA_UNKNOWN_PROFILE_EXCHANGE` | A mapping names no uniquely resolved required exchange in its profile function. |
| `CA_UNKNOWN_SPECIFIC_FUNCTION` | A mapping names no declared specific function key. |
| `CA_UNKNOWN_SPECIFIC_EXCHANGE` | A mapping names no declared exchange key in its specific function. |
| `CA_MAPPING_FIELD_INCOMPATIBLE` | A mapping field cannot be owned by the selected profile destination. |
| `CA_MAPPING_VALUE_TYPE` | An explicit mapped decision value has the wrong scalar type. |
| `CA_CONTEXT_ASSERTION_MISMATCH` | A context assertion decision disagrees with explicit completion target context. |
| `CA_MATERIALIZATION_INCOMPLETE` | A required scaffold field remains unresolved, so no contract is emitted. |
| `CA_UNMAPPED_AUTHOR_DECISION` | An explicit author decision lacks a typed mapping, so no contract is emitted. |
| `CA_SERIALIZATION_ROUNDTRIP` | Rendered JSON/YAML cannot be parsed back to the validated materialized model. |
| `CA_OUTPUT_EXISTS` | Output destination exists and `--force` was not supplied. |
| `CA_OUTPUT_PATH` | Output parent or destination violates the safe path policy. |
| `CA_OUTPUT_WRITE` | Exclusive creation or safe replacement write failed. |

`CA_*` applies only to the completion workspace. Materialization preconditions
use `CA_*`; materialized-contract validation surfaces `SC_*` and selected OMS
profile validation surfaces `OP_*` unchanged.

Capability completion also reports `CA_CAPABILITY_SCHEMA` (invalid artifact),
`CA_DUPLICATE_CAPABILITY_KEY`, `CA_UNKNOWN_CAPABILITY_KEY`,
`CA_UNKNOWN_CAPABILITY_ROLE`, and `CA_INACTIVE_CAPABILITY_FUNCTION`. Typed
Capability fields reuse `CA_MAPPING_VALUE_TYPE`, including strict Boolean
validation for `requires_position_information`.

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

## UCI resolver (`UR_*`)

`UR_*` means the failure is owned by UCI XSD parsing or resolver semantics.
Resolver orchestration can surface `SC_*`, `SS_*`, or `UR_*` depending on the
layer that owns the failure: invalid contracts retain `SC_*`; manifest,
composition, and verified-byte failures retain `SS_*`; only resolver-owned
failures receive `UR_*`.

| Code | Meaning |
| --- | --- |
| `UR_XML_PARSE` | Verified XSD bytes are malformed XML or rejected by defused XML parsing. |
| `UR_XSD_DOCUMENT` | Parsed XML is not a usable `xs:schema` document or lacks `targetNamespace`. |
| `UR_PRIMITIVE_METADATA` | Direct `UCI_PRIMITIVE:` metadata is duplicate or normalizes to empty. |
| `UR_TYPE_QNAME` | A message `type` value is missing, malformed, or has an unknown namespace prefix. |
| `UR_UNKNOWN_TYPE` | A resolved type QName has no matching global declaration. |
| `UR_AMBIGUOUS_TYPE` | A resolved type QName has multiple matching global declarations. |
| `UR_UNKNOWN_MESSAGE` | A contract OMS Message has no global UCI message candidate. |
| `UR_AMBIGUOUS_MESSAGE` | A contract OMS Message has multiple global UCI message candidates. |

## Inputs/Outputs projection (`IP_*`)

`IP_*` means the failure is owned by the fail-closed join between an already
prepared contract and resolved OMS entries. Preparation failures retain their
`SC_*`, `SS_*`, or `UR_*` identity.

| Code | Meaning |
| --- | --- |
| `IP_UNEXPECTED_RESOLUTION` | A resolved OMS entry has no matching contract OMS exchange. |
| `IP_AMBIGUOUS_RESOLUTION` | More than one resolved entry matches one contract OMS exchange. |
| `IP_MESSAGE_MISMATCH` | Matching function/exchange IDs have different contract and resolved message names. |
| `IP_MISSING_RESOLUTION` | A contract OMS exchange has no resolved entry. |
