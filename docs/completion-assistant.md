# Capability completion boundary

Capability facts are never inferred from completion evidence, message names, or
function names. Optional Capability structure and typed author decisions are
consumed by the scaffold/materializer; omission remains unknown rather than an
empty portable inventory.

# Completion assistant

`tools/completion_assistant.py` renders a deterministic, non-normative authoring
worksheet from a completion input and a validated OMS profile:

```bash
python tools/completion_assistant.py \
  --input examples/completion/ir-search-and-track.yaml \
  --decisions examples/completion/ir-search-and-track-decisions.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format markdown
```

Use `--format json` for reference-tool JSON. Normal stdout contains only the
requested rendering. Invalid input, invalid profiles, or incompatible target
versions return nonzero and write `FAIL <diagnostic>` to stderr.

## Evidence candidates and author decisions

`schema/tooling/completion/v0.1/completion-input.schema.json` is tooling-only,
not part of the portable Service Contract schema hierarchy. It requires a target
context (`contract_version`, `oms_version`, and explicit `service_kind`), a
source registry, and unconfirmed scalar candidates. Candidate `target` values
are opaque deterministic authoring labels, not JSONPath or contract-edit
instructions. `null` and arbitrary object values are not allowed.

Sources retain one of `published_contract`, `published_supporting_doc`,
`implementation`, or `oms_normative`. These categories are labels, not numeric
confidence or a ranking. Duplicate source/candidate IDs and unknown candidate
sources are rejected with `CA_*` diagnostics.

Candidates sharing a target are retained. Distinct values require an explicit
author decision; identical values from multiple sources also remain separate
provenance records. The assistant never selects, ranks, or treats a candidate as
authored contract semantics.

`schema/tooling/completion/v0.1/completion-decisions.schema.json` defines an
optional, separate author-decision overlay. Each opaque worksheet `target` has at
most one decision, which uses exactly one of `select_candidate` or scalar
`value`. A selected candidate retains that exact evidence record and provenance.
An explicit value is author intent only and has no fabricated source provenance,
even when it equals an observed candidate. Decision diagnostics reject malformed
documents, duplicate targets, unknown candidate IDs, and candidate-target
mismatches.

The stages remain distinct: an **evidence candidate** is an observed possible
value; an **author decision** is explicit intent recorded against a worksheet
label; an **authored contract semantic** is a value actually written to and
 validated in a portable Service Contract. Task 036 implements only the first two
stages. Task 037 adds a separate typed mapping and profile-derived scaffold;
 see [completion-scaffold.md](completion-scaffold.md). Task 038 adds the separate
 fail-closed [materializer](completion-materialization.md): scaffold output remains
 tooling-only, while successful materializer stdout is a validated portable
 Service Contract. None of these tools executes JSONPath, patches, or applies a
 contract.

Task 039 adds optional explicit specific-function structure; it is separate from
both evidence and decisions. See [completion-specific-functions.md](completion-specific-functions.md).

## Profile and Capability boundary

The selected profile is loaded through existing profile validation. Its fixed
requirements applicable to the explicit target component kind are displayed
separately from candidate evidence. The assistant does not match candidates to
requirements or claim satisfaction.

For Services and Subsystems, it asks the author to confirm the Capability
inventory as unknown, explicitly zero, or one-or-more. It does not infer that
inventory from message/candidate names and does not apply Section 3.3 rules.
Isolators receive no Capability-inventory prompt or Section 3.3 requirements.

This tool performs no source extraction, scraping, LLM inference, contract
generation, contract editing, candidate-to-profile satisfaction analysis, or
Capability inference.

Task 041 adds a separate explicit traceability artifact. Candidate provenance and
profile citations remain evidence/rule rationale, not portable traceability; see
[completion-traceability.md](completion-traceability.md).
