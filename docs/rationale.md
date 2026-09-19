# Rationale and Repository Justification

This document explains *why* a separate machine-readable Service Contract repository is useful, what problem it solves, and which tempting alternatives were rejected.

It is informative. Normative syntax/semantics are defined by the JSON Schema and `docs/specification.md`.

## 1. The problem is not message code generation alone

Generating programming-language types from UCI schemas addresses one part of an OMS integration problem: it tells a program what a `ServiceStatus`, `PositionReport`, or another UCI-defined message looks like.

It does not answer the service-specific questions:

- Does this Service consume or produce the message?
- Which function uses it?
- Is it mandatory or optional for that function?
- Which topic/configuration is used?
- Is it asynchronous, on demand, or periodic?
- Is the exchange an OMS Message at all, or is it a Data Transfer, Special Signal, or Security Exchange?

Those are Service Contract questions.

A code generator that only sees UCI has the entire vocabulary but does not know the Service's allowed/required subset.

## 2. Human-readable contracts are necessary but awkward as generator inputs

The official OMS Service Contract template and instructions are designed to communicate integration information and support the OMS process. They are not designed as a stable compiler front-end.

Trying to generate code directly from a DOCX/PDF table would introduce brittle concerns:

- document layout parsing;
- merged cells and formatting changes;
- prose normalization;
- table-header changes between revisions;
- difficulty distinguishing human formatting from semantic content; and
- poor source-control diffs for service interface changes.

A machine-readable companion is not a replacement for the human contract. It is a normalized representation that tools can validate deterministically.

## 3. Why not put this in `oms_ada`?

Doing so would make Ada the de facto owner of a language-neutral architectural concept. Rust, C++, Python, deployment tooling, and documentation tooling would then have poor choices:

- depend conceptually on an Ada repository;
- copy/fork the schema; or
- invent incompatible representations.

The contract format is upstream of all language backends, so it deserves a language-neutral home.

## 4. Why not put this in `oms_rust`, `oms_cpp`, or Sleet?

The same argument applies. Runtime transport, deployment authorization, and language bindings are consumers of the Service Contract; they are not the right owner for its portable semantics.

Sleet configuration, for example, can be a useful derived artifact because it authorizes/defines what a deployed service may publish or subscribe to. But deployment authorization is only one projection of the richer Service Contract and should not become the architecture's source of truth.

## 5. Why not make the generator repository the specification repository?

This is a closer alternative and may be acceptable for a private prototype, but separation provides long-term advantages:

### Independent lifecycle

A schema clarification should not require releasing the code generator, and a generator optimization should not imply a specification change.

### Multiple consumers

A validator, documentation generator, IDE extension, compliance tool, or deployment generator can consume the spec without adopting the implementation language or dependency tree of the main generator.

### Conformance fixtures

One repository can hold portable valid/invalid examples against which every implementation is tested.

### Clear compatibility declarations

A generator can say explicitly:

```text
contract language: 0.1
OMS profiles:       2.5
UCI schemas:        2.5, 2.6 (subject to explicit compatibility support)
```

without conflating those version streams.

## 6. Why YAML plus JSON Schema?

YAML is proposed as the authoring surface because it is:

- readable in code review;
- friendly to comments;
- easy to generate/transform;
- supported by editors; and
- straightforward to map to JSON data models.

JSON Schema supplies a language-independent structural contract and editor tooling.

The normative data model is JSON-compatible. A producer may serialize it as JSON if desired; YAML is the recommended human authoring syntax.

## 7. Why not store message primitive in the contract?

Because the OMS Service Contract material makes Message Primitive UCI-owned metadata. In the pinned public UCI 2.5 XSD it is represented by `UCI_PRIMITIVE:` documentation metadata. Copying it would create two sources of truth:

```text
UCI says:      Command-2
contract says: Status-1
```

A resolver would then need an arbitrary rule for which one wins.

Instead, the contract records the message reference, and resolution enriches the internal model from UCI. A mismatch becomes impossible because there is no duplicate primitive field to drift.

This is a general rule for the project:

> Store service-specific facts here; resolve standardized message-definition facts from their authoritative schema.

## 8. Why make source traceability first-class?

The format is meant to bridge architecture documents and generated software. Traceability helps reviewers answer:

- Why is this function present?
- Where did this mandatory exchange come from?
- Which revision of the Service Contract instructions was used?
- Was an interface decision taken from AMS GRA, OMS, UCI, a platform ICD, or a program-specific source?

Traceability metadata is not executable behavior, but it is valuable engineering evidence and makes later audits/updates much less ambiguous.

## 9. Why distinguish contract-language version from OMS/UCI versions?

They solve different problems.

`contract_version` answers: “Which grammar and semantics parse this YAML?”

`oms_version` answers: “Which OMS rules/profile apply?”

`uci_schema_version` answers: “Against which message schema are OMS Message references resolved?”

`service.version` answers: “Which implementation release does this contract describe?”

`ams_gra_version`, when present, answers: “Which AMS GRA architecture context does this artifact claim to target?”

No one of these should imply another.

## 10. Why represent timing but not enforce it?

The OMS Service Contract has timing-category and timing-value columns, so omitting them would lose useful integration information.

However, the v2.5 instructions identify the nominal/max timing columns as informative. Automatically converting them into hard deadlines, assertions, SPARK contracts, scheduling requirements, or pass/fail tests would strengthen the upstream semantics without authorization.

Therefore v0.1 preserves the values and category but deliberately leaves enforcement to a separate explicit policy or a future normative timing model.

## 11. Why start with function I/O rather than workflow/state machines?

The Service Contract includes richer behavioral sections: preconditions, workflow/orchestration, postconditions, and error handling. Formalizing those could eventually enable very powerful generation and verification.

But arbitrary English does not become formal semantics by putting it in YAML.

A good future behavioral language would need:

- a defined expression model;
- well-defined state ownership;
- event semantics;
- ordering/concurrency semantics;
- error/timeout semantics;
- mappings to multiple programming languages; and
- an explicit relationship to OMS requirements.

Starting with the I/O contract gives immediate value while avoiding a false impression of formal verification.

## 12. Expected benefits

### Stronger generated APIs

A backend can generate only the typed inputs/outputs declared by a Service rather than exposing the entire UCI universe.

### Cross-language consistency

Ada/SPARK, Rust, C++, and Python consume the same service declaration.

### Deployment consistency

Topic/message allowlists can be derived from the same declaration used to generate source interfaces.

### Better tests

Contract tests can verify that every mandatory declared exchange has a generated surface and that undeclared output paths are not accidentally exported by the generated façade.

### Better reviewability

A service interface change is a small structured diff:

```diff
+ - id: position-report-input
+   direction: input
+   message: PositionReport
```

rather than a change inferred from several language implementations and deployment files.

### Better documentation

Inputs/Outputs tables and interface summaries can be generated from the same source that drives code generation.

## 13. Costs and risks

A new specification has real costs:

- another versioned artifact to maintain;
- risk of drifting from upstream OMS/GRA/UCI releases;
- risk of over-modeling fields before they are needed;
- risk of accidentally presenting an independent format as official.

Mitigations in this repository include:

- explicit non-authoritative status notices;
- upstream source links;
- small v0.1 scope;
- no duplication of UCI primitive/type information;
- conformance fixtures;
- independent standard-version fields; and
- a requirement that semantic changes cite upstream material or a concrete interoperability need.

## 14. Success criteria for v0.1

This repository is useful if two independent generator backends can consume the same contract and agree on:

- function identity;
- exchange kind;
- direction;
- mandatory/optional status;
- message reference/topic;
- timing category/metadata; and
- source traceability,

while resolving message structure/primitive independently from the same UCI schema.

It is not necessary for v0.1 to reproduce every page of an OMS Service Contract to achieve that goal.
