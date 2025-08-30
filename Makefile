PY ?= python3
APP ?= obsidian_to_hugo

.PHONY: all fmt lint type test cov run build docker sec sbom convert watch

all: fmt lint type test

fmt:
	ruff format

lint:
	ruff check --output-format=github
	ruff check --select I --fix
	ruff format --check

type:
	mypy src

test:
	pytest -q --cov=src --cov-report=term-missing

cov:
	coverage html && echo "see htmlcov/index.html"

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8080

build:
	$(PY) -m build

sec:
	bandit -r src || true
	pip-audit -r requirements.txt || true

sbom:
	syft . -o cyclonedx-json > sbom.json

e2e:
	pytest -q tests/e2e

convert:
	$(PY) -m obsidian_to_hugo convert

watch:
	$(PY) -m obsidian_to_hugo watch

gui:
	$(PY) -m obsidian_to_hugo --gui

install:
	pip install -e .[dev]