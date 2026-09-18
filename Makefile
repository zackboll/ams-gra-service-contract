PYTHON ?= python3

.PHONY: validate test check

validate:
	$(PYTHON) tools/validate.py --all

test:
	$(PYTHON) -m pytest -q

check: validate test
