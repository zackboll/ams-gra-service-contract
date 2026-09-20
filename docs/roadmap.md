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
- portable v0.1 machine-readable conformance corpus, schema semantic fingerprint
  guard, YAML/JSON equivalence vectors, and independent-consumer compatibility
  handoff.

Explicitly out of scope:

- Complete UCI type-layout parsing (verified source loading, global message/type
  declaration identity, namespace-aware QName resolution, and primitive extraction
  are implemented; type contents are intentionally not);
- code generators;
- behavioral DSL;
- formal proof semantics.

## Candidate v0.2 — Resolver/profile conformance hooks

Potential goals driven by real implementation experience:

- completion workspace manifest, unified completion CLI, workspace-relative
  artifact resolution, and materialization-readiness check implemented; no
  portable semantics added.
- first end-to-end real published-service completion workspace exercise
  implemented: RF FM Demod is exercised through pinned evidence, decisions,
  mapping, workspace, scaffold, and fail-closed readiness. It is intentionally
  not materialized because unresolved author semantics remain.
- real service-owner answer loop simulated end-to-end: the same RF published
  evidence plus explicitly labelled simulated owner decisions, specific-function
  topology, and explicit zero Capabilities materializes a valid portable,
  OMS-profile-validated contract. This is not an official RF FM Demod contract;
  actual service-owner confirmation remains future work.
- completion-assistant foundation implemented: a provenance-preserving,
  non-normative worksheet displays unconfirmed evidence candidates,
  profile-derived requirements, and an explicit author-decision overlay without
  changing core schema semantics or acting as an independent downstream
   consumer. Typed candidate/decision-to-destination mapping, profile-derived
   required-function authoring scaffold, and structural missing-field reporting
    are implemented. Specific-function structural authoring, typed mapping,
    scaffold, and fail-closed portable contract materialization, SC validation of
     materialized output, and OMS profile validation of materialized output are
      implemented. Capability declaration completion/materialization, Section
     3.3 per-Capability required-function scaffold/materialization, and
     conditional component-level Position Information Processing are implemented.
     Capability-owned optional/domain-specific exchanges, Capability-owned
      Specific Functions if needed, deterministic YAML serialization — implemented,
      safe complete-contract file emission — implemented, semantic apply/edit
      workflow, candidate-to-profile
    satisfaction analysis, consumer feedback reconciliation,
   a second independent consumer, and broader independent consumers
    remain pending;
- explicit namespace-qualified contract syntax only if real integrations require it;
- deterministic local source extraction assistance, raw-byte verification, regex
  capture/assertion, JSON/YAML pointers, and RF FM Demod recipe — implemented
  first slice; richer structured selectors remain evidence-driven pending and
  optional AI-assisted extraction is future evaluation only;
- OMS-version-specific profile validation hooks (OMS 2.5 Required Service
  Function inventory, minimum Service Initialization and Service Status exchange
  shapes, Required Subsystem Function inventory, and minimum Subsystem Status
   exchange shape implemented; Subsystem Shutdown Table 3.2-6 source
   classification completed (all substantive rows are removable green guidance,
   so no Shutdown exchange minimum); Subsystem State Command Processing source
   classification completed (fixed command minimum implemented; status direction
   conflict documented); Subsystem BIT Table 3.2-4 source classification
   completed (all seven substantive rows are removable green guidance, so no BIT
   Calibration Table 3.2-5 source classification
   completed (all seven substantive rows are removable green guidance, so no
   Calibration exchange minimum); Subsystem Startup Table 3.2-1 source
   classification completed (all five substantive rows and all three MDF
   acquisition examples are removable green guidance, so no Startup exchange
    minimum or fixed alternative-set rule); Required Capability-related Function
    Section 3.3 inventory semantics classified, with explicit Capability
    identity/presence, function ownership, and position-dependency facts needed
    before exact per-Capability function validation; exchange-table
    classification completed: both Table 3.3-1 position-report rows are
    removable green guidance in all matcher-owned fields, while fixed prose
    establishes only a conceptual alternative without machine-checkable
    cardinality; Capability identity/presence/ownership and position-dependency
    facts remain needed for conditional function validation; deliberately
    designed conditional-function and alternative-exchange semantics remain
     pending only if later fixed evidence requires them; Table 3.3-2 Capability
     and Capability Status classification completed: its ESM rows are removable
     green examples, while mixed generic prose establishes only
     Capability-relative output/periodic family semantics; explicit Capability
     identity/presence/ownership remains required before exact enforcement;
     Table 3.3-3 Capability Enable/Disable classification completed: its ESM
     command/status rows are removable green examples, while mixed generic prose
     establishes Capability-relative command input, status output, and response
     behavior only; Capability identity/ownership and separate response-pair
      behavioral modeling remain future boundaries; Table 3.3-4 Capability
      Operations classification completed: its ESM `Entity`/`SignalReport` and
      PO/POST `ProductMetadata`/`ProductLocation`/`ImageFile` groups are
      removable green domain examples in all matcher-owned fields, so no
      universal Operations exchange minimum; all Section 3.3 exchange tables
      (3.3-1 through 3.3-4) now have explicit evidence classifications, but
        portable Capability identity/presence, ownership, position dependency,
        bounded standard role identity, Capability-relative profile selectors,
        per-Capability required-function validation, and conditional
        component-level Position Information Processing are implemented; required
        alternative-exchange semantics (unless later evidence requires them),
        response relationships, preconditions/postconditions, behavior/state
        modeling, broader real Service Contract exercises, and profile coverage
        remain pending);
- richer Data Transfer metadata if required by real contracts;
- generated Inputs/Outputs table projection (initial non-normative reference
  projection implemented; DOCX/template adaptation remains later work);
- canonical contract/profile, schema-source, UCI resolver, and Inputs/Outputs
  projection diagnostic families implemented across the primary reference
  pipeline;
- real Service Contract exercises, mature diagnostics, and first independent
  downstream consumers. An initial real UCI 2.5 -> 2.6 resolver/schema
  transition has been exercised; broader upstream-version mapping remains.
  Published real-world OMS 2.5 Service Contract evidence now covers five
  artifacts: RF FM Demod, Graupel, IR Search and Track, Supercell, and Squall
  OMS Adapters. The survey favors author-confirmed source-documentation/
  completion assistance; it does not weaken authored-contract semantics or mark
  the independent-consumer 1.0 criterion complete. Broader examples are still
  needed before introducing a separate partial-observation model.

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
- upstream-version mapping has been tested across at least one OMS update or
  carefully simulated transition (the UCI 2.5 -> 2.6 resolver/schema exercise is
  initial evidence, not completion of this broader OMS-inclusive criterion);
- extension/version policy is stable;
- diagnostics and conformance fixtures are mature; and
- the project can make a clear compatibility commitment.

`ams-gra-codegen-oms` is being developed as an independent consumer and has a
portable v0.1 handoff corpus. That work does not itself complete the two
independent-consumer criterion; feedback reconciliation and a second independent
consumer remain pending, as do semantic apply/edit workflow,
and pre-materialization profile evidence comparison implemented; it reports exact
alignment between candidates and fixed OMS profile facts without making
profile-conformance claims. `OP_*` validation of a materialized contract remains authoritative.
