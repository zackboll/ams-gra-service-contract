PYTHON ?= python3

.PHONY: validate text-check test check

validate:
	$(PYTHON) tools/validate.py --all

text-check:
	$(PYTHON) tools/check_text_hygiene.py

test:
	$(PYTHON) -m pytest -q

check: text-check validate test
