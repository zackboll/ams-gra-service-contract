# OMS profile evidence comparison

`profile-evidence` is tooling-only analysis between published service evidence and fixed OMS normative profile facts. Explicit links name an opaque completion target and one exact profile fact; target spelling never creates a link.

It reports `aligned` or `conflicting` candidates and `all_aligned`, `all_conflicting`, or `mixed` observed alignment. Disagreement is report data, not a diagnostic. An optional author decision is likewise reported as `aligned`, `conflicting`, or `no_decision`.

This is not compliance validation. Only `OP_*` validation of a materialized portable contract establishes profile conformance. Links do not select candidates, create decisions or mappings, mutate the scaffold, or mutate a contract.

Supported fixed facts are required-function `name`, `category`, `required_group`, and single-value `applicability`; and required-exchange `kind`, `selector`, `direction`, `mandate`, and `timing_kind`. Facts such as topics and numeric rates remain normal evidence/authoring work.
