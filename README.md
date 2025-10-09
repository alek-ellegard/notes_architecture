# Architecture patterns

## [orchestration with domains and callbacks](/orchestration/base-domain/README.md)

## [singleton patterns](/patterns/singleton-patterns/README.md)

**TLDR:**

- Comparison of
  - **`__new__` override** vs **module-level** singleton patterns,

> demonstrating why module-level approach prevents silent data corruption and provides thread-safe initialization.

**Approaches:** [approach1_new_override.py](/patterns/singleton-patterns/src/singleton_patterns/approach1_new_override.py) (problematic) vs [approach2_module_level.py](/patterns/singleton-patterns/src/singleton_patterns/approach2_module_level.py) (recommended)
