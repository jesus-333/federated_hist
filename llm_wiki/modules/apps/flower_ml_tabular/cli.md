# `apps/flower_ml_tabular/cli.py`

## `main_ml_tabular(args, flwr_args) -> None`

Verbatim copy of [`flower_hist/cli.py:main_hist`](../flower_hist/cli.md) with only the function name changed.
It still :
- calls `write_debug_config(7, "flower_hist")`;
- defaults to `./config/hist.toml`;
- validates `app == 'flower_hist'`;
- passes `--run-config "app='flower_hist' ..."`.

No console script or function in `clinnova_fl/cli.py` calls it.

## To make it usable

- Replace the app name with the canonical ML app name (to be unified across `LIST_OF_APPS`, `apps/server.py`, `apps/client.py`, `config/__init__.py:DEBUG_CONFIG_PATH`).
- `DEBUG_CONFIG_PATH['flower_ml']` points to `debug_config/ml.toml`, which does not exist (the file is `ml_tabular.toml`).
- The synthetic debug connector must produce labels (`n_classes >= 2`) for training.
- Add an entry in `clinnova_fl/cli.py` (e.g. `flower_ml_tabular()`) and a console script in `pyproject.toml` (hyphenated name, e.g. `clinnova-ml-tabular`).
