# Completion assistant

`tools/completion_assistant.py` renders a deterministic, non-normative authoring
worksheet from a completion input and a validated OMS profile:

```bash
python tools/completion_assistant.py \
  --input examples/completion/ir-search-and-track.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format markdown
```

Use `--format json` for reference-tool JSON. Normal stdout contains only the
requested rendering. Invalid input, invalid profiles, or incompatible target
versions return nonzero and write `FAIL <diagnostic>` to stderr.

## Completion input

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

Candidates sharing a target are retained. Distinct values are an explicit author
decision; identical values from multiple sources also remain separate provenance
records. The assistant never selects, accepts, confirms, ranks, or treats a
candidate as authored contract semantics.

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
generation, contract editing, or author confirmation.
