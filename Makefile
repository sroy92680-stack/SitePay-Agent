# Repository policy check
.PHONY: check test

check:
	python scripts/check_project_rules.py .

test:
	python -m pytest -q scripts/tests
