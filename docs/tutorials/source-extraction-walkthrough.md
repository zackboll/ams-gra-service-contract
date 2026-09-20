# Source extraction walkthrough

```
SOURCE FILES -> exact hashes + explicit selectors -> EXTRACTION RECIPE
-> UNCONFIRMED COMPLETION INPUT -> WORKSHEET -> AUTHOR DECISIONS
-> SCAFFOLD / CHECK -> PORTABLE CONTRACT
```

Run the synthetic example:

```bash
python tools/completion.py extract tests/fixtures/completion-extraction/recipe.yaml \
  --source-root tests/fixtures/completion-extraction/source --format yaml
```

You write the source registry, hashes, opaque candidate targets, locators, and exact selectors. Extraction saves typing recovered values. You still write decisions because evidence is not contract semantics. Changed upstream bytes fail hash verification; ambiguous regexes fail rather than picking a match. It infers neither Capabilities nor functions. Feed the resulting completion input into a workspace and start at `worksheet`.

For RF FM Demod, manually clone and checkout `af13bd2926b15253e795920c91320733a29927ea`, then run the same command with `examples/completion/rf-fm-demod-extraction.yaml` and `--source-root /tmp/rf-fm-demod`. CI never performs this clone.
