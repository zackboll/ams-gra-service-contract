# Roadmap

This roadmap is directional and does not promise release dates.

## Implemented through repository/tooling v0.2.0

- Portable contract language `0.1`, JSON Schema validation, YAML/JSON support,
  traceability, Capabilities, and a 64-case conformance pack.
- OMS 2.5 profile validation, including service/subsystem and Capability
  inventory coverage.
- UCI 2.5 and 2.6 schema-source manifests and resolver transition evidence.
- Optional, fail-closed completion workspaces, materialization, extraction, and
  profile-evidence comparison.
- Real-shaped published-evidence exercises, including the clearly labelled
  simulated RF FM Demod owner-answer example.

These are project-defined experimental companion representation and reference
tooling, not OMS/UCI standards or code generation.

## Future evidence-driven work

After repository/tooling v0.2.0, major portable-contract changes should be
driven primarily by downstream consumer feedback, additional OMS versions, or
confirmed real-contract requirements. Likely work includes consumer feedback
reconciliation, actual service-owner confirmation, a second independent
consumer, a future OMS version profile, and richer extraction selectors or
semantic apply/edit only if demanded. New portable fields or contract-language
versions should not be speculative.

Complete UCI type-layout parsing remains separate work for a downstream binding,
code generator, or reusable schema library if real consumers demonstrate need.
Behavior/state semantics remain intentionally absent.

## 1.0 criteria and current evidence

| Criterion | Status |
| --- | --- |
| Two independent consumers | Not complete; code generation is a separate consumer repository. |
| Multiple real examples | Partial, with substantial published evidence but no confirmed owner contract. |
| Upstream version transition | UCI 2.5 -> 2.6 exercised; OMS transition not yet. |
| Extension/version policy | Initial policy implemented. |
| Diagnostics/conformance | Substantial pre-1.0 coverage. |

The project is not declaring 1.0 readiness.
