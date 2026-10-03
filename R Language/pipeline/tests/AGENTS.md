# tests/ — rules layer

Inherits the root rules, see [../../../AGENTS.md](../../../AGENTS.md).

Constraints specific to `tests/`:

- Every test corresponds to a failure that actually happened — no coverage padding
- Do not test implementation details; test the behaviour that broke
- When a bug is fixed, add the test in the same commit
- Run with `uv run pytest -q` from `R Language/pipeline/`

What each file covers is documented in [README.md](README.md), not here.
