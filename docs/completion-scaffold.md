# Completion authoring scaffold

`tools/completion_scaffold.py` combines a validated completion input, separate
author decisions, a typed mapping, and a validated OMS profile into deterministic
Markdown or JSON tooling output. It writes only stdout and never creates,
modifies, or validates a portable Service Contract.

```bash
python tools/completion_scaffold.py --input examples/completion/ir-search-and-track.yaml \
  --decisions examples/completion/ir-search-and-track-decisions.yaml \
  --mapping examples/completion/ir-search-and-track-mapping.yaml \
  --profile profiles/oms/2.5/profile.yaml --format markdown
```

The stages are intentionally separate: **candidate → decision → mapping →
scaffold → future contract**. Mapping targets are opaque labels; destinations,
not target-string parsing, define executable meaning. The scaffold marks values
as `completion_target`, `oms_profile`, `author_decision`, or `missing`; selected
candidates retain source/provenance while direct author values do not fabricate it.

Optional `--specific-functions` adds only author-declared specific topology;
keys never generate IDs or names. It creates no Capability functions, generates no IDs/topics, and makes no
profile-satisfaction or compliance claim. Unmapped decisions remain visible.
Task 038's separate materializer consumes this tooling-only scaffold fail-closed;
it is the semantic boundary where successful stdout becomes a portable contract.

Optional `--capabilities` adds explicit Capability topology. Omission is
`unknown`, `capabilities: []` is `explicit_empty`, and a non-empty structure is
`declared`; these states remain distinct. The validated OMS profile plus resolved
Capability facts determines Section 3.3 function topology, never names or
messages. Capability IDs/names and function IDs/names remain author decisions.

Optional `--traceability` adds explicit adopted portable sources and trace lists to
the tooling scaffold. It neither adopts candidate evidence nor copies profile
traceability automatically.
