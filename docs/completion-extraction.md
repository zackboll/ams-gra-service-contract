# Deterministic completion source extraction

`completion.py extract` is offline transcription assistance: exact local source bytes plus explicit rules produce **unconfirmed completion candidates**. It does not create decisions, mappings, function/Capability structure, profile claims, or a contract.

A `completion-extraction` recipe has a target, ordered source registry, and ordered rules. Each source carries ordinary completion provenance plus a relative `local_path` and raw-byte SHA-256. `--source-root` must exist; paths cannot be absolute, escape with `..`, or be symlinks. The tool reads each verified file once and never fetches its `uri`.

Supported extractors are `text_regex_capture` (one match and a named capture; explicit `string`, finite JSON `number`, or exactly `true`/`false` Boolean), `text_regex_assert` (one matching authored evidence assertion emits its explicit scalar), and RFC-6901 `structured_pointer` over JSON/YAML (scalar only). Regex defaults have no flags; only explicit `multiline` and `dotall` are supported. Zero or multiple matches fail.

Successful output has existing `completion_version: "0.1"`, ordered sources/rules, and strips paths, hashes, and selectors. It is round-tripped and validated against the existing completion-input schema before stdout or `--output`; `--force` uses the shared safe atomic writer. Failures emit no output and use `CA_EXTRACTION_*` diagnostics.

Use the generated file as the `input` of a normal completion workspace, then run `worksheet`. Extraction removes transcription effort, not author responsibility.
