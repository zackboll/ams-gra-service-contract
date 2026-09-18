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

- UCI XSD resolver implementation;
- code generators;
- behavioral DSL;
- formal proof semantics.

## Candidate v0.2 — Resolver/profile conformance hooks

Potential goals driven by real implementation experience:

- standardized schema-source manifest/digest representation;
- deterministic extension-schema namespace resolution rules;
- OMS-version-specific profile validation hooks;
- richer Data Transfer metadata if required by real contracts;
- generated Inputs/Outputs table projection;
- canonical diagnostic codes.

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
