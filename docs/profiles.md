# Profile validation

The v0.1 service-contract schema is a portable grammar, not an OMS-version
conformance checklist. `contract_version`, OMS version, UCI version, and a
profile version are independent. OMS-specific requirements therefore live in
opt-in, machine-readable profile manifests rather than in
`schema/v0.1/service-contract.schema.json`.

## OMS 2.5 required-service profile

`profiles/oms/2.5/profile.yaml` is profile format version `0.1`, profile ID
`oms-2.5`, and supports contract version `0.1`. Its source is OMSC-INS-003
Rev M, *OMS Service Contract Instructions v2.5*, dated 2026-01-22, pinned to
upstream OMS commit `726272bd0390982a759c91a9cf4e13b81c2b510b`.

Section 3.1 says every OMS Service must provide the Required Service Functions
and that the section also applies to Isolators. Sections 3.1.1 and 3.1.2 say
that **Service Initialization** and **Service Status**, respectively, are
required for Services and Isolators. The profile consequently requires exactly
one function with each exact name for `service` and `isolator`, with
`category: required`, `required_group: service`, and
`applicability: applicable`.

Subsystem applicability is conditional on a Platform-hosted Adapter and other
upstream facts unavailable in v0.1 contracts. This initial profile does not
infer those facts and does not unconditionally enforce these functions for
`subsystem`.

Use it explicitly:

```bash
python tools/validate.py \
  --profile profiles/oms/2.5/profile.yaml \
  my-complete-service.yaml
```

The validator rejects unsupported contract versions and OMS-version mismatch
before treating the profile as applicable. It matches standard functions by
their exact upstream canonical `function.name`, not local `function.id` or
traceability prose. A future contract version may introduce explicit
standard-function identity if real consumers show that name matching is
insufficient.

For the uniquely matched **Service Status** function, the profile additionally
requires these minimum OMS-message exchange shapes, regardless of local
function/exchange IDs or declaration order:

- `ServiceStatus`: output, mandatory, periodic;
- `ServiceStatusDataRequest`: input, mandatory, asynchronous; and
- `ServiceStatusDataRequestStatus`: output, mandatory, on-demand.

Additional valid exchange rows are allowed. The profile intentionally does not
fix topics, operational attributes/SOAC selection, subscription groups,
numerical timing values, Appendix C content, contract traceability, or UCI
message primitives. It does not yet validate Service Initialization exchange
inventory, complete Required Subsystem Function inventory, complete
capability-related Function inventory, or workflow/state behavior.

## Partial reference examples

Files in `examples/` can be intentionally partial, source-backed function
demonstrations. Ordinary v0.1 validation does not mean OMS profile completeness.
For example, `examples/service-status.yaml` is a valid, source-backed v0.1
fragment but is not a complete OMS Service contract and is expected to fail the
whole-service OMS 2.5 profile.

Future profiles can evolve independently for OMS 2.6 or additional conformance
rules without changing the portable v0.1 grammar.
