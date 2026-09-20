# Release checklist

Before tagging a repository/tooling release, verify:

- portable schema fingerprint verified;
- conformance pack passes;
- all schema-source manifests validate;
- OMS profile validates;
- all tests and text hygiene pass;
- `git diff --check` passes;
- support manifest validates;
- versioning documentation is consistent;
- CHANGELOG has one `## [Unreleased]` section and release notes are prepared;
- consumer handoff is reviewed; and
- portable schema changes are explicitly classified.

The release gate is:

```bash
make check PYTHON=.venv/bin/python
python tools/conformance.py check conformance/v0.1/manifest.json
python tools/release_check.py compatibility/support-v0.2.0.json
git diff --check
```

After merge, manually create the tag and GitHub release, record the immutable
release commit, and update a downstream consumer pin if desired. This checklist
does not create tags, publish artifacts, or mutate metadata.
