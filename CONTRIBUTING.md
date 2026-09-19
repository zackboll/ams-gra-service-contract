# Contributing

Thank you for helping improve the machine-readable Service Contract experiment.

## Principles

Changes should preserve four boundaries:

1. this repository specifies a portable contract format, not a language backend;
2. UCI-owned message-definition facts should be resolved from UCI, not copied here;
3. upstream semantics should be represented faithfully and cited; and
4. new fields should have concrete semantics and a demonstrated consumer/use case.

## Change checklist

For a schema or semantic change:

- explain the use case/rationale;
- cite the upstream AMS GRA/OMS/UCI source when claiming to represent upstream behavior;
- update `docs/specification.md`;
- update `schema/v*/service-contract.schema.json`;
- add/update valid examples;
- add at least one invalid fixture when the change creates a new rejection rule;
- update validator logic if the rule is cross-field/semantic;
- update `CHANGELOG.md`;
- run `make check`.

## Upstream source hierarchy

Prefer official public source artifacts. Implementation repositories/tutorials are useful evidence but should be clearly identified as non-normative examples.

Do not infer a portable requirement solely from one runtime implementation.

## Backward compatibility

During 0.x development, breaking changes may occur, but they must be explicit. Do not silently change the interpretation of an existing v0.1 field while leaving `contract_version` unchanged.

If a change makes previously valid documents invalid or changes their meaning, discuss whether it requires a new contract-language version.

## Tests

Install dependencies and run:

```bash
make check
```

This includes repository text hygiene checks for UTF-8 encoding, LF line
endings, final newlines on non-empty text files, and no trailing whitespace.

A new semantic rule should normally have both positive and negative coverage.

## Documentation style

Use precise architectural terminology. Distinguish clearly among:

- AMS GRA architecture;
- OMS Service Contract semantics;
- UCI message/schema semantics;
- CAL/runtime behavior; and
- this independent representation.

Avoid wording that implies official status or endorsement.
