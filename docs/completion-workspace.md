# Completion workspace

A completion workspace is a tooling-only manifest that names the artifacts in one authoring exercise. It does not merge evidence, author decisions, mappings, structure, or portable contract fields. It only saves repeatedly spelling out filenames.

```yaml
workspace_version: "0.1"
input: complete-service.yaml
decisions: complete-service-decisions.yaml
mapping: complete-service-mapping.yaml
profile: ../../profiles/oms/2.5/profile.yaml
```

The only fields are `workspace_version`, `input`, `profile`, `decisions`, `mapping`, `specific_functions`, `capabilities`, and `traceability`. Version, input, and profile are required. Every configured path is a nonempty relative literal resolved from the workspace's directory; absolute paths, `~`, environment expansion, and globbing are rejected. `..` is supported.

| Command | Required entries |
| --- | --- |
| `worksheet` | input, profile |
| `scaffold`, `check`, `materialize` | input, profile, decisions, mapping |

Specific functions, capabilities, and traceability are optional for later stages. `worksheet` works without decisions. `check` prepares and validates the same in-memory contract as materialization but never serializes or writes. `materialize --format {yaml,json}` reuses safe `--output`/`--force` behavior.

```bash
python tools/completion.py worksheet service-workspace.yaml
python tools/completion.py scaffold service-workspace.yaml
python tools/completion.py check service-workspace.yaml
python tools/completion.py materialize service-workspace.yaml --format yaml --output contract.yaml
```

Workspace errors are `CA_WORKSPACE_*`; artifact, portable-contract, and profile diagnostics retain their existing `CA_*`, `SC_*`, and `OP_*` identities. OMS-codegen consumes only the resulting portable `contract.yaml`, never a workspace or its authoring artifacts.
