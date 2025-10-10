.PHONY: benchmark benchmark-compare benchmark-save clean

run: 
	uv run src/data_structures/dataclass_vs_native.py
# Run benchmarks
benchmark:
	uv run pytest tests/ -v --benchmark-only

# Run benchmarks and compare with previous results
benchmark-compare:
	uv run pytest tests/ -v --benchmark-compare

# Run benchmarks and save results for comparison
benchmark-save:
	uv run pytest tests/ -v --benchmark-only --benchmark-save=baseline

# Clean up benchmark results
clean:
	rm -rf .benchmarks

# Show help
help:
	@echo "Available targets:"
	@echo "  benchmark         - Run all benchmarks"
	@echo "  benchmark-compare - Run and compare with previous results"
	@echo "  benchmark-save    - Run and save results as baseline"
	@echo "  clean            - Remove benchmark results"
	@echo "  help             - Show this help message"
