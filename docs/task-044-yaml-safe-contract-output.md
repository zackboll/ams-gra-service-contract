# Task 044 — Deterministic YAML and safe contract output

Task 044 adds portable deterministic YAML serialization and complete-contract
file emission to `tools/completion_materialize.py`; it does not alter the v0.1
schema, `contract_version`, or materialization semantics.

```bash
python tools/completion_materialize.py \
  --input examples/completion/complete-service.yaml \
  --decisions examples/completion/complete-service-decisions.yaml \
  --mapping examples/completion/complete-service-mapping.yaml \
  --profile profiles/oms/2.5/profile.yaml \
  --format yaml \
  --output /tmp/service-contract.yaml

ams-gra-codegen-oms service-plan \
  --contract /tmp/service-contract.yaml \
  --schema /path/to/UCI_MessageDefinitions_v2_5_0.xsd
```

This is a documentation-only OMS-codegen handoff. This repository neither
depends on nor invokes OMS-codegen. `--force` replaces the whole validated
contract, never edits, patches, merges, or preserves comments from an existing
document.
