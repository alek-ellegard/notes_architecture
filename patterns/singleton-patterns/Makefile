.PHONY: help sync install test test-verbose test-cov test-parallel lint lint-fix type-check demo clean format all

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

sync:  ## Sync dependencies with uv (recommended)
	uv sync

install:  ## Install package and dev dependencies (legacy)
	uv venv
	uv pip install -e ".[dev]"

test:  ## Run tests
	uv run pytest

test-verbose:  ## Run tests with verbose output
	uv run pytest -v

test-cov:  ## Run tests with coverage report
	uv run pytest --cov=singleton_patterns --cov-report=term-missing --cov-report=html

test-parallel:  ## Run tests in parallel with xdist
	uv run pytest -n auto

test-approach1:  ## Test approach 1 problems
	uv run pytest tests/test_approach1_problems.py -v

test-approach2:  ## Test approach 2 advantages
	uv run pytest tests/test_approach2_advantages.py -v

lint:  ## Check code with ruff
	uv run ruff check src/ tests/

lint-fix:  ## Fix code issues with ruff
	uv run ruff check src/ tests/ --fix

format:  ## Format code with ruff
	uv run ruff format src/ tests/

type-check:  ## Run mypy type checking
	uv run mypy src/

demo:  ## Run the demonstration script
	uv run python demo.py

clean:  ## Clean build artifacts and cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage .venv/

all: clean sync lint type-check test  ## Clean, sync, lint, type-check, and test

ci: lint type-check test-cov  ## Run CI checks (lint, type-check, test with coverage)
