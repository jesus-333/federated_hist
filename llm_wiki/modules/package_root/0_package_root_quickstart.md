# Package root (`clinnova_fl/`) — quickstart

Files directly inside `src/clinnova_fl/` (not in a sub-module).

| File | Purpose | Page |
|------|---------|------|
| `__init__.py` | Package docstring only (no exports, no `__version__`). | — |
| `cli.py` | Console entry points (`clinnova-hist`) and the debug-config generator `write_debug_config`. | [`cli.md`](./cli.md) |

Console scripts are declared in `pyproject.toml` :
```toml
[project.scripts]
clinnova-hist = "clinnova_fl.cli:flower_hist"
```

Only `clinnova-hist` exists. There is no entry point for the ML tabular app yet (its `cli.py` exists but is not wired, see [`../apps/flower_ml_tabular/cli.md`](../apps/flower_ml_tabular/cli.md)).
