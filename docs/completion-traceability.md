# Completion traceability authoring

Task 041 adds tooling-only `completion-traceability.schema.json`. The sequence is
`evidence source -> explicit author adoption -> portable source -> explicit trace
attachment -> portable function/exchange traceability`.

`sources[].key` is local to this artifact and resolves `traces[].source_key`; it
never appears in portable JSON. Authors must separately provide portable `id` and
explicitly select `from_completion_source`. Title, URI, and an existing evidence
revision are copied exactly; title/URI cannot be overridden. A supplied revision
must equal known evidence revision. Evidence provenance and evidence notes are not
portable metadata. Source and per-target trace declaration order are preserved.

Supported targets are required function/exchange, specific function/exchange,
per-Capability function, and component Capability function. Unknown or inactive
targets fail rather than disappearing; a function trace on a `not_applicable`
function remains valid. Omitting `--traceability` preserves previous output; an
empty artifact omits `sources`.

This does not convert candidate provenance or OMS profile citations into contract
traceability. Downstream consumers such as OMS-codegen may later use explicitly
authored citations for generated-file provenance, documentation, diagnostics, or
auditing; this task defines no code-generation behavior.
