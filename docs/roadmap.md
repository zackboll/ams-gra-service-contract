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
       portable Capability identity/presence, ownership, and position dependency
       are implemented; Capability-relative profile selectors,
       conditional-function rules, per-Capability required-function validation,
       any required alternative-exchange semantics, and response/behavior
       relationships remain pending; broader real Service Contract exercises and
       profile coverage remain);
- richer Data Transfer metadata if required by real contracts;
- generated Inputs/Outputs table projection (initial non-normative reference
  projection implemented; DOCX/template adaptation remains later work);
- canonical contract/profile, schema-source, UCI resolver, and Inputs/Outputs
  projection diagnostic families implemented across the primary reference
  pipeline;
- real Service Contract exercises, mature diagnostics, and first independent
  downstream consumers. An initial real UCI 2.5 -> 2.6 resolver/schema
  transition has been exercised; broader upstream-version mapping remains.

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
