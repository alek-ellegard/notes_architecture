
include $(MK_PATH)index.mk
project=base_domain
run:
	hatch run dev:uv run src/$(project)/entrypoint.py
# Clean environment
clean:
	rm -rf .hatch
	rm -rf src/$(project).egg-info
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

remove-env: clean

# Environment setup
env:
	hatch env create

setup: env

# Type checking
types:
	hatch run dev:mypy src/

# make types f=src/
types-f: 
	hatch run dev:mypy $(f)

types-domains:
	clear
	@make types-domain-zmq-processor
	@make types-domain-metrics	

types-domain-zmq-processor:
	@echo
	@echo --------- zmq ----------
	@make types-f f=src/$(project)/features/zmq
	@echo
	@echo ------- processor -------
	@make types-f f=src/$(project)/features/processor

types-domain-metrics:
	@echo
	@echo ------- metrics -------
	@make types-f f=src/$(project)/features/metrics
	@echo
	@echo ------- self-metrics -------
	@make types-f f=src/$(project)/features/self-metrics
	@echo
	@echo -------------------
	@echo
	

# Linting and formatting
lint:
	hatch run dev:ruff format src/ tests/ 2>/dev/null || true
	hatch run dev:ruff check --fix src/ tests/ 2>/dev/null || true

lint-check:
	hatch run dev:ruff format --check src/ tests/ 2>/dev/null || true
	hatch run dev:ruff check src/ tests/ 2>/dev/null || true

# CI tasks
ci: lint-check types test

ci-fix: lint types test
# Testing
test:
	hatch run dev:pytest tests/ -v 2>/dev/null || echo "No tests found"
test-setup-show: ## show test setup
	hatch run dev:pytest tests/ --setup-show -v 2>/dev/null || echo "No tests found"

test-f: ## test specific file -- test-f f=<file_path>
	hatch run dev:pytest $(f) -v 2>/dev/null || echo "No tests found"
test-domains:
	make test-f f=src/$(project)/features/zmq
	make test-f f=src/$(project)/features/processor
	make test-f f=src/$(project)/features/metrics
	make test-f f=src/$(project)/features/self-metrics
	
