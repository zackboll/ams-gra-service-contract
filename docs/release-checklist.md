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

`release_check.py` is an offline, fast, repository-local metadata gate. It
validates the local compatibility surfaces named by
`compatibility/support-v0.2.0.json`, including UCI schema-source baselines; it
does not parse external UCI source bytes or replay resolver regression.

The release gate is:

```bash
make check PYTHON=.venv/bin/python
python tools/conformance.py check conformance/v0.1/manifest.json
python tools/release_check.py compatibility/support-v0.2.0.json
git diff --check
```

For stronger pre-release external-byte evidence, acquire source roots matching
the exact revisions pinned by `schema-sources/uci/2.5/manifest.yaml` and
`schema-sources/uci/2.6/manifest.yaml`, then run:

```bash
python tools/uci_version_regression.py \
  --uci-25-source-root /path/to/pinned-uci-2.5 \
  --uci-26-source-root /path/to/pinned-uci-2.6
```

This separate resolver regression parses verified pinned UCI bytes and checks
the cross-version counts and continuity-message probe set.

After merge, manually create the tag and GitHub release, record the immutable
release commit, and update a downstream consumer pin if desired. This checklist
does not create tags, publish artifacts, or mutate metadata.
