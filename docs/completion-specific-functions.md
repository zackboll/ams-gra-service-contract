# Specific-function authoring

Specific-function structure is tooling-only explicit author intent. It declares
which specific functions and exchanges exist, their membership, and exchange
kind. `key` values are bounded local identities: they are never copied to a
portable function or exchange ID.

`decisions` are selected/supplied field values; structure is object topology;
mapping connects an opaque decision target to a typed topology field. A message,
topic, direction, source section, or ordering never creates or groups functions.
Use `--specific-functions` with scaffold or materialize. Applicable specific
functions require explicit ID, name, applicability, and kind-required exchange
fields. `not_applicable` requires a reason and emits no exchanges.
