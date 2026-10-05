# `clinnova_fl/apps/__init__.py`

Defines the registry of app names :
```python
LIST_OF_APPS = [
    "flower_hist",
    "flower_k_means",
    "flower_ml_tabular",
]
```

Used by :
- `apps/server.py` to validate `context.run_config["app"]`;
- `apps/client.py` in error messages.

When adding a new app, append its name here (it must equal the folder name and the string used in `server.py`/`client.py` dispatching).

## Known issues

- `"flower_k_means"` has no implementation.
