PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: install dev lint typecheck test audit run-api run-gui run-dashboard clean

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements-dev.txt

lint:
	ruff check navil tests scripts

typecheck:
	mypy navil tests scripts

test:
	pytest tests/ -v --cov=navil --cov-report=term-missing

audit:
	pip-audit

run-api:
	uvicorn navil.api.server:app --host 0.0.0.0 --port 8080 --reload

run-gui:
	$(PYTHON) -m navil

run-dashboard:
	$(PYTHON) -m navil

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage dist build
