# Roadmap

This roadmap is directional and does not promise release dates.

## v0.1 — Function I/O contract foundation

Goals:

- YAML/JSON authoring model;
- JSON Schema validation;
- explicit OMS/UCI versions;
- Service/function identity;
- Required/Specific function category;
- applicability;
- OMS Message, Data Transfer, Special Signal, Security Exchange, and Non-OMS Message kinds;
- input/output direction;
- mandatory/optional Level of Mandate;
- asynchronous/on-demand/periodic timing metadata;
- source traceability;
- local semantic validator;
- conformance fixtures.

Explicitly out of scope:

- Complete UCI type-layout parsing (verified source loading, global message/type
  declaration identity, namespace-aware QName resolution, and primitive extraction
  are implemented; type contents are intentionally not);
- code generators;
- behavioral DSL;
- formal proof semantics.

## Candidate v0.2 — Resolver/profile conformance hooks

Potential goals driven by real implementation experience:

- explicit namespace-qualified contract syntax only if real integrations require it;
- OMS-version-specific profile validation hooks (OMS 2.5 Required Service
  Function inventory, minimum Service Initialization and Service Status exchange
  shapes, Required Subsystem Function inventory, and minimum Subsystem Status
  exchange shape implemented; Subsystem Startup source classification/exchanges,
  State Command Processing exchanges, BIT exchanges, Calibration exchanges,
  Shutdown exchanges, Required Capability-related Functions, and broader profile
  coverage remain);
- richer Data Transfer metadata if required by real contracts;
- generated Inputs/Outputs table projection (initial non-normative reference
  projection implemented; DOCX/template adaptation remains later work);
- initial canonical contract/profile validation diagnostic codes implemented;
  schema-source, resolver, and projection code families remain;
- real Service Contract exercises, cross-version validation, mature diagnostics,
  and first independent downstream consumers.

A full UCI type-layout parser is not an implied next milestone. It would require
substantial XSD support (content models, inheritance, members, cardinality,
attributes, restrictions, anonymous types, imports/includes, and built-ins) and
belongs in a downstream binding/code-generator or separate reusable
language-neutral schema library only if real consumers demonstrate that need.

## Candidate v0.3 — Behavioral model exploration

Only after multiple v0.1 consumers exist, evaluate a deliberately small behavioral language for:

- named service states;
- event-triggered transitions;
- machine-readable preconditions;
- machine-readable postconditions;
- required response relationships;
- error outcomes.

Any such model must define concurrency/order semantics before being advertised as formal/executable behavior.

Potential uses:

- Ada/SPARK contracts;
- Rust/C++ runtime checks;
- state-machine skeleton generation;
- sequence/conformance test generation.

## Candidate pre-1.0 — Skill/MEL composition

Evaluate whether a broader AMS GRA artifact should model relationships among:

- OMS Service exchanges;
- MEL/MFA dependencies;
- Local Function MPU interfaces;
- Skill composition.

This may belong in a *different* specification rather than expanding the Service Contract format. The project should not conflate those architecture layers merely for convenience.

## 1.0 criteria

Consider 1.0 only after:

- at least two independent language/tool consumers exist;
- the format has been exercised against multiple real Service Contract examples;
- upstream-version mapping has been tested across at least one OMS update or carefully simulated transition;
- extension/version policy is stable;
- diagnostics and conformance fixtures are mature; and
- the project can make a clear compatibility commitment.
