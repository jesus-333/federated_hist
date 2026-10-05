# `clinnova_fl/apps/server.py`

Root Flower `ServerApp`.
It is the server component declared in `pyproject.toml` and the single server entry point of every run.

## Objects and functions

### `app = ServerApp()`

### `@app.main() main(grid : Grid, context : Context) -> None`

Steps :
1. Check `"app"` is in `context.run_config` and in `LIST_OF_APPS`, otherwise `ValueError`.
2. Check `"path_app_config"` is in `context.run_config`.
3. `app_config = read_toml_config(Path(context.run_config["path_app_config"]))`.
4. `app_config['simulation'] = context.run_config['simulation']` (so the flag reaches clients via `custom_config`).
5. Require `"dataset_id"` in `app_config` (the `dataset_id` key in `run_config`/`pyproject.toml` is currently **not** used: the dataset id comes from the app TOML).
6. Build :
    ```python
    experiment_config = dict(
        app        = context.run_config["app"],
        app_config = app_config,
        dataset_id = dataset_id,
        simulation = context.run_config['simulation'],
    )
    ```
7. `server = return_server_module(app)` and call `server.main(grid, context, experiment_config)`.

Logging uses `flwr.common.logger.log` with `INFO`/`DEBUG`.

### `read_toml_config(path_toml_config : Path) -> dict`

`toml.load` wrapped in a `try` that re-raises as `ValueError` with the path.

### `return_server_module(app_name : str)`

Lazy import of `clinnova_fl.apps.<app>.server`.
Branches: `flower_hist`, `flower_ml_tabular`, `flower_k_means`.

## Notes

- `run_with_nvflare` from `run_config` is not propagated into `app_config`/`experiment_config`, so `apps/client.py` never sees it (the NVFlare branch there is unreachable in practice).
- `simulation` passed via CLI is the string `'true'` (`--run-config "simulation='true'"`), not a boolean. It is truthy, which is what the client checks.
- Line 50 uses `f" ... {context.run_config["app"]}"` (same quote type nested), which requires Python >= 3.12.

## Known issues

- `main` has an empty docstring.
