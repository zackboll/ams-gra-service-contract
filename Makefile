PYTHON ?= python3

.PHONY: validate text-check schema-source-check conformance-check release-check test check

validate:
	$(PYTHON) tools/validate.py --all

text-check:
	$(PYTHON) tools/check_text_hygiene.py

schema-source-check:
	$(PYTHON) tools/schema_sources.py validate schema-sources/uci/2.5/manifest.yaml
	$(PYTHON) tools/schema_sources.py validate schema-sources/uci/2.6/manifest.yaml

conformance-check:
	$(PYTHON) tools/conformance.py check conformance/v0.1/manifest.json

release-check:
	$(PYTHON) tools/release_check.py compatibility/support-v0.2.0.json

test:
	$(PYTHON) -m pytest -q

check: text-check schema-source-check validate conformance-check release-check test
