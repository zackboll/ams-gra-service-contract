# Machine-Readable Service Contract Specification v0.1

**Status:** Experimental / pre-1.0
**Normative scope:** This document defines the semantics of `contract_version: "0.1"`. The JSON Schema in `schema/v0.1/service-contract.schema.json` defines its structural constraints.

This specification is an independent companion format intended to represent a subset of information from an OMS Service Contract in a machine-readable form. It is not an official AMS GRA, OMS, or UCI specification.

## 1. Conformance terminology

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be interpreted as described by RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

A **v0.1 contract document** conforms when it:

1. parses as YAML 1.2-compatible data or JSON;
2. validates against the v0.1 JSON Schema;
3. satisfies the semantic rules in this document; and
4. uses `contract_version: "0.1"`.

A **resolved contract** additionally has all OMS Message references resolved against the declared UCI baseline schema and declared UCI extension schemas.

Resolution consumes only the immutable verified schema-byte snapshot. It indexes direct global message and type declarations, resolves each primitive-tagged message's XSD `type` QName using that document's XML namespace declarations, and requires exactly one global type declaration with the resulting expanded QName. This identifies declaration identity only; type content/layout interpretation remains out of scope.

Conformance of this file format does **not** imply conformance of a Service to AMS GRA, OMS, UCI, a platform, a mission package, or any acquisition/compliance requirement.

## 2. Source model and design boundary

The format is based on a deliberate separation of responsibility:

| Information | Authoritative source for a consumer | Represented in v0.1? |
|---|---|---:|
| Which function an exchange belongs to | Machine-readable service contract | Yes |
| Input vs output | Machine-readable service contract | Yes |
| Mandatory vs optional for the function | Machine-readable service contract | Yes |
| Data-exchange kind | Machine-readable service contract | Yes |
| OMS message name/topic | Machine-readable service contract | Yes |
| Periodicity class and informative values | Machine-readable service contract | Yes |
| UCI message structure | Selected UCI schema | No |
| UCI message primitive | Selected UCI schema | No |
| Language-specific types | Generator/backend | No |
| Runtime CAL implementation details | Deployment/runtime configuration | No, except topic/configuration metadata represented by the Service Contract |

The OMS Service Contract material describes the Message Primitive as UCI-owned metadata. In the public UCI 2.5 XSD pinned by this repository, message declarations expose that value through `xs:documentation` entries of the form `UCI_PRIMITIVE: Status-1.`. A conforming v0.1 producer therefore **MUST NOT require authors to duplicate the message primitive** in this file format.

## 3. Document root

A contract document contains four required root members and one optional member:

```yaml
contract_version: "0.1"
service: { ... }
standards: { ... }
sources: [ ... ]     # optional
functions: [ ... ]
```

Unknown root members are rejected by the schema. This is deliberate: silent acceptance of misspelled architectural fields is undesirable.

### 3.1 `contract_version`

`contract_version` identifies **this machine-readable format**, not OMS, UCI, AMS GRA, or the Service implementation.

For this specification it MUST be exactly:

```yaml
contract_version: "0.1"
```

Consumers MUST reject unsupported contract-language versions.

## 4. `service`

`service` identifies the implementation described by the contract.

```yaml
service:
  name: example-service
  version: "1.2.3"
  kind: service
  description: Optional human-readable description.
```

### 4.1 `name`

A non-empty human-readable Service name. The OMS Service Contract instructions require a unique Service name for communication/integration purposes; consumers SHOULD preserve this value in generated documentation and diagnostics.

### 4.2 `version`

The implementation version of the described Service. This is independent of all standard/schema versions.

### 4.3 `kind`

One of:

- `service`
- `subsystem`
- `isolator`

The OMS v2.5 Service Contract instructions state that the Service Contract template applies to Subsystems, Services, and Isolators, using “Service” generically in that document. v0.1 makes that distinction explicit.

### 4.4 `description`

Optional human-readable text. A generator MUST NOT infer executable behavior from this field.

## 5. `standards`

`standards` records the versions against which the contract is authored.

```yaml
standards:
  oms_version: "2.5"
  uci_schema_version: "2.5"
  uci_extension_schemas:
    - vendor-extension-1.0
  ams_gra_version: "..."   # optional
```

### 5.1 `oms_version`

The OMS specification version relevant to this contract.

### 5.2 `uci_schema_version`

The baseline UCI message-schema version against which OMS Message references are resolved.

The OMS Service Contract instructions require the Service Contract environment/message-set information to identify the baseline OMS Message Schema version and describe it as an official UCI Schema release. v0.1 captures that relationship here.

### 5.3 `uci_extension_schemas`

An optional ordered list of logical extension-schema identifiers. A declared value
MUST match exactly one supplied extension schema-source manifest whose `id` is
byte-for-byte equal to that value. Matching is case-sensitive; it MUST NOT use
case folding, substring matching, filenames, repository URIs, or inferred paths.

Every declared identifier MUST have a manifest, and a toolchain MUST reject an
undeclared supplied extension manifest. The contract contains logical identities
only; it MUST NOT contain manifest paths, source revisions, hashes, or XSD
namespace details.

Declaration order defines the deterministic order of the composed schema-source
set after its baseline. It is an ordering for loading, display, and reproducible
composition only. It MUST NOT define symbol override precedence: neither an
extension over the baseline nor a later extension over an earlier extension may
silently win a message-name conflict.

A resolver MUST NOT silently search arbitrary schemas when a message is absent from the declared schema set.

### 5.4 `ams_gra_version`

Optional AMS GRA version/context identifier. It is not inferred from OMS or UCI versions.

## 6. `sources`

`sources` is an optional registry of source artifacts used for traceability.

```yaml
sources:
  - id: oms-sc-instructions-v25
    title: OMS Service Contract Instructions
    document_number: OMSC-INS-003
    revision: M
    date: "2026-01-22"
    uri: https://github.com/open-arsenal/oms/...
    note: Optional note
```

### 6.1 Source IDs

Each `sources[].id` MUST be unique within the document. IDs are local stable handles used by `traceability` entries.

### 6.2 Source URIs

A URI SHOULD identify the exact upstream document/revision where practical. A repository moving branch is useful for navigation but is weaker traceability than an immutable tag or commit. Consumers MAY warn when a source URI is not immutable.

### 6.3 No incorporation by reference

A source link provides traceability. It does not cause arbitrary text from the linked document to become executable semantics of this contract.

## 7. `traceability`

Functions and exchanges may include traceability records:

```yaml
traceability:
  - source: oms-sc-instructions-v25
    locator: "Service Status / Inputs and Outputs"
    note: Optional explanation of the mapping
```

`source` MUST resolve to a `sources[].id` in the same document.

`locator` and `note` are descriptive. Tools MUST NOT infer executable semantics from prose in these fields.

## 8. `functions`

`functions` is the service-function inventory represented by the machine-readable contract.

```yaml
functions:
  - id: service-status
    name: Service Status
    category: required
    required_group: service
    applicability: applicable
    exchanges: []
```

### 8.1 `id`

Machine-stable local identifier. Function IDs MUST be unique within the document.

### 8.2 `name`

Human-readable function name.

### 8.3 `category`

One of:

- `required`
- `specific`

This preserves the minimum category split described by the OMS Service Contract function-list guidance.

### 8.4 `required_group`

Optional refinement for a required function:

- `service`
- `subsystem`
- `capability`

This field is a convenience for tooling/document generation and is not a replacement for the official template's organization. It MUST NOT be present when `category: specific`.

### 8.5 `applicability`

One of:

- `applicable`
- `not_applicable`

A `not_applicable` function MUST include `not_applicable_reason` and MUST contain no exchanges.

This permits a machine-readable document to preserve an explicit N/A decision when useful. A producer MAY omit unrelated functions entirely if its workflow does not require round-trip regeneration of template sections.

### 8.6 `description`

Optional prose. It is informative to machines unless a future specification explicitly defines a behavioral language.

### 8.7 `exchanges`

An ordered list of input/output exchanges associated with the function. Ordering is for stable display/diff generation and MUST NOT be interpreted as runtime execution order.

## 9. Exchange common semantics

Every exchange has:

- `id`
- `kind`
- `direction`
- `mandate`
- `timing`
- optional `traceability`

Exchange IDs MUST be unique within their containing function.

### 9.1 `direction`

Exactly one of:

- `input`
- `output`

The upstream Service Contract instructions require two unique rows when the same message is both an input and an output. v0.1 mirrors that rule structurally: one exchange object has exactly one direction. Authors MUST create separate exchange objects to represent both directions.

### 9.2 `mandate`

Exactly one of:

- `mandatory`
- `optional`

This maps to OMS Service Contract **Level of Mandate (LoM)**.

`mandatory` means the input/output is necessary to perform the function as described by the upstream Service Contract semantics. `optional` means it enhances the function but is not necessary for normal function execution.

A consumer MUST NOT reinterpret `mandatory` as, by itself:

- a compile-time language requirement;
- a proof obligation;
- a safety integrity level;
- a hard real-time deadline; or
- a platform authorization policy.

A code generator MAY have an explicit backend policy that turns mandatory exchanges into required stubs or abstract methods, provided that policy is documented separately.

### 9.3 `kind`

Maps to the OMS Service Contract Data Exchange (DE) category:

| v0.1 | OMS table concept |
|---|---|
| `oms_message` | OMS Message (`M`) |
| `data_transfer` | Data Transfer (`DT`) |
| `special_signal` | Special Signal (`SS`) |
| `security_exchange` | Security Exchange (`SE`) |
| `non_oms_message` | Non-OMS Message (blank DE in the upstream table) |

## 10. OMS Message exchange

Example:

```yaml
- id: status-output
  kind: oms_message
  direction: output
  mandate: mandatory
  message: ServiceStatus
  topic: ServiceStatus
  operational_attribute: SOAC-1
  timing:
    kind: periodic
    nominal_rate_hz: 1.0
```

### 10.1 `message`

The UCI/OMS message name referenced by the exchange.

A **resolved contract** requires this value to resolve uniquely in the declared UCI baseline plus declared extension schemas.

The message's structure and primitive are not defined by this string alone; they come from the selected UCI schema.

### 10.2 `topic`

The specific topic name/configuration value represented in the Service Contract Data Exchange Information column for an OMS Message.

A runtime CAL implementation may have additional deployment-specific addressing or authorization. Those deployment details are not implied unless explicitly represented by the contract/toolchain.

### 10.3 `operational_attribute`

Optional operational-attribute/configuration token associated with the topic.

### 10.4 `subscription_group`

Optional subscription-group information when the Service Contract uses it.

### 10.5 `appendix_c_mapping`

Optional human/document-generation mapping token. It has no executable semantics in v0.1.

## 11. Data Transfer exchange

Example:

```yaml
- id: image-input
  kind: data_transfer
  direction: input
  mandate: mandatory
  name: Sensor Image Stream
  protocol: ExampleProtocol
  data_type: Image
  data_format: ExampleFormat
  sharing_pattern: ExamplePattern
  timing:
    kind: asynchronous
```

The upstream Service Contract instructions describe Data Transfer information using protocol, Data Type, Data Format, and Sharing Pattern. v0.1 records those values as strings without trying to standardize the external protocols themselves.

A consumer MUST NOT invent transfer semantics based only on matching strings.

## 12. Special Signal exchange

Example:

```yaml
- id: discrete-input
  kind: special_signal
  direction: input
  mandate: mandatory
  name: Example Special Signal
  reference: Example interface document
  timing:
    kind: asynchronous
```

v0.1 intentionally keeps Special Signal metadata shallow. `details` and `reference` are informational. A later version may add typed semantics based on demonstrated tooling needs and upstream definitions.

## 13. Security Exchange

Example:

```yaml
- id: security-info-input
  kind: security_exchange
  direction: input
  mandate: mandatory
  name: Example Security Exchange
  timing:
    kind: asynchronous
```

v0.1 identifies the exchange and its Service Contract metadata but does not define authorization, cryptographic, classification, labeling, or cybersecurity-policy semantics.

## 14. Non-OMS Message

Example:

```yaml
- id: legacy-input
  kind: non_oms_message
  direction: input
  mandate: optional
  name: ExampleLegacyMessage
  reference: Non-OMS Messages table entry
  timing:
    kind: asynchronous
```

The OMS v2.5 Service Contract instructions specify that the DE column is left blank for a Non-OMS Message and that the Data Exchange Name should match the corresponding entry in the Non-OMS Messages section. v0.1 uses the explicit `non_oms_message` discriminator so the machine representation does not depend on a semantically meaningful blank cell. `details` and `reference` are informational.

## 15. Timing

OMS Service Contract periodicity is represented by a discriminated `timing` object.

### 15.1 Asynchronous

```yaml
timing:
  kind: asynchronous
```

Maps to the upstream asynchronous/aperiodic category (`A`): exchanges occur at an irregular, non-periodic rate.

### 15.2 On demand

```yaml
timing:
  kind: on_demand
  nominal_response_seconds: 0.5
  max_response_seconds: 3.0
```

Maps to the upstream on-demand category (`OD`). The numeric fields represent the corresponding Service Contract timing columns when supplied.

### 15.3 Periodic

```yaml
timing:
  kind: periodic
  nominal_rate_hz: 1.0
  max_rate_hz: 0.5
```

Maps to the upstream periodic category (`P`). The numeric fields represent the corresponding Service Contract rate columns when supplied.

### 15.4 Informative status of numeric timing values

The OMS v2.5 Service Contract instructions mark the nominal/max response/rate columns **INFORMATIVE (not normative)**. v0.1 preserves that status.

Therefore:

- tools MUST NOT automatically interpret these values as hard deadlines;
- tools MUST NOT automatically emit proof contracts from them;
- tools MUST NOT assume a numerical ordering relationship that the upstream table does not define;
- tools MAY display them, carry them into generated documentation, and expose them to explicit backend policies.

A future version may add a separate, explicitly normative timing-requirement model. Such a model must not retroactively change v0.1 timing semantics.

## 16. Message primitive resolution

v0.1 has no `primitive` field for an OMS Message. The resolver validates the
contract, composes its baseline and declared extension manifests, reads and
verifies the local bytes of every selected manifest file, then retains that
verified byte snapshot for XSD parsing. Only files explicitly listed by those
manifests contribute definitions; parsing MUST NOT trust a later filesystem read.

A resolver performs conceptually:

```text
contract exchange.message
        |
        v
selected UCI schema set
        |
        +--> resolve message definition
        |
        +--> read UCI_PRIMITIVE: documentation metadata
        |
        v
ResolvedExchange
  message = ...
  primitive = ...
```

The implemented resolver indexes only direct `xs:element` children of an
`xs:schema` document with a `targetNamespace`. A global element is a UCI message
declaration for this slice only when its own direct `xs:annotation` has exactly
one direct `xs:documentation` item beginning `UCI_PRIMITIVE:`. Its non-empty
value is trimmed, one final prose period is removed, and the resulting value
must remain non-empty. Nested elements, inline type annotations, and global
elements without that marker are not indexed. This is message identity and
primitive extraction, not full XSD type-system resolution.

For an unqualified contract message name, the resolver MUST find all indexed
global message declarations whose local name equals `exchange.message` in the
selected schema-source set. The candidate count has fail-closed semantics: zero candidates
MUST fail as unknown, one candidate resolves, and more than one candidate MUST
fail as ambiguous. It MUST NOT select a candidate based on baseline versus
extension role, extension declaration order, manifest input order, file order,
or filesystem order.

XSD declarations are fundamentally identified by XML Schema expanded names. The
derived primitive and expanded name are resolver output, not persisted into the
contract. v0.1
contract message references remain local names only. Therefore
`{namespace-A}ExampleMessage` and `{namespace-B}ExampleMessage` make
`message: ExampleMessage` ambiguous. v0.1 does not add namespace-qualified
message syntax; a future need for it requires a reviewed contract-language
change. Multiple manifests sharing a target namespace are not invalid merely due
to namespace equality; uniqueness concerns the resolved declaration.

A producer MUST NOT add a private `primitive` property to bypass resolution; unknown fields are intentionally rejected.

## 17. Required Service Functions

The OMS v2.5 Service Contract material identifies Required Service Functions that every OMS Service is required to provide, including Service Initialization and Service Status, subject to the upstream tailoring/applicability rules.

This v0.1 schema does **not** hard-code the complete OMS function catalog. The reasons are:

1. required-function catalogs belong to a particular OMS version;
2. this contract language must remain independently versioned;
3. future OMS versions may change the catalog; and
4. a resolver/profile validator can apply OMS-version-specific requirements more accurately than a generic syntax schema.

A production OMS-aware validator SHOULD load a profile for the selected `oms_version` and verify required functions/applicability separately.

## 18. Semantic validation rules

After JSON Schema validation, a conforming repository validator MUST enforce at least:

1. source IDs are unique;
2. function IDs are unique;
3. exchange IDs are unique within each function;
4. every traceability source reference resolves to a source registry entry.

A UCI-aware resolver additionally MUST enforce message resolution as described above.

Future validators may add diagnostics that do not change acceptance semantics. A warning MUST NOT silently become a rejection in the same contract-language version without a specification update.

## 19. Round-trip and canonicalization

v0.1 does not define a canonical YAML serialization.

Tools SHOULD preserve:

- function ordering;
- exchange ordering;
- human-readable descriptions; and
- source traceability

when round-tripping, because stable diffs are a principal use case.

Tools MUST NOT rely on YAML mapping key order for semantics.

## 20. Security considerations

Contracts may influence generated interfaces and deployment configuration. Consumers should treat contract files as source code:

- validate before generation;
- reject unknown fields;
- pin or verify external schema inputs where reproducibility matters;
- avoid fetching arbitrary URIs merely because they appear in `sources`;
- do not execute text from `description`, `note`, `details`, `locator`, or `reference`; and
- treat generated deployment permissions as security-sensitive outputs requiring review.

## 21. Extensibility policy

v0.1 intentionally rejects unknown fields rather than offering an unrestricted extension map. This keeps the experimental core small and makes typos visible.

When a real integration need requires additional data, prefer a reviewed specification change with:

1. an upstream source or concrete tooling use case;
2. precise semantics;
3. schema changes;
4. valid/invalid fixtures; and
5. compatibility analysis.

This policy may be revisited after the core format stabilizes.
