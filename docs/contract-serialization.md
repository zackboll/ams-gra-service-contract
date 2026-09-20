# Contract serialization

The completion materializer serializes one complete portable v0.1 Service
Contract in either deterministic JSON or deterministic YAML. JSON is the
machine-friendly serialization; YAML is the human-friendly serialization. Both
encode exactly the same portable contract model.

YAML uses repository-owned `JsonCompatibleYamlDumper`: UTF-8-compatible LF text,
one final newline, two-space block indentation, insertion-order mappings, no key
sorting, aliases, anchors, Python tags, or non-finite floats. It round-trips
through `JsonCompatibleYamlLoader` without YAML 1.1 scalar coercion.

`render_json()` and `render_yaml()` are pure render helpers. Before either stdout
or file output, the materializer parses the exact text, compares it to the
materialized model, and reruns portable `SC_*` and selected profile `OP_*`
validation.

```bash
python tools/completion_materialize.py \
  --input examples/completion/complete-service.yaml \
  --decisions examples/completion/complete-service-decisions.yaml \
  --mapping examples/completion/complete-service-mapping.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format yaml
```

Without `--output`, the complete serialization is written to stdout. With
`--output PATH`, successful output is written only to that file. Existing files
are refused by default. `--force` replaces an existing regular file by writing,
flushing, and fsyncing a same-directory temporary file before `os.replace`.
Missing parents, directories, and symlink destinations are rejected. New files
use exclusive creation. This is a practical filesystem boundary, not a claim of
protection against a malicious concurrent directory modifier.
