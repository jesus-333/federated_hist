# `apps/flower_ml_tabular/cli.py`

## `main_ml_tabular(args, flwr_args) -> None`

Same structure as [`flower_hist/cli.py:main_hist`](../flower_hist/cli.md), adapted to the ML app :
- `--debug` → `write_debug_config(7, "flower_ml_tabular")` (template `debug_config/ml_tabular.toml`);
- default config path `./config/ml_tabular.toml` (this file does not exist in the repo root `config/` folder);
- validates `app == 'flower_ml_tabular'`;
- passes `--run-config "app='flower_ml_tabular' path_app_config='<path>'"`.

No console script or function in `clinnova_fl/cli.py` calls it yet.

## Remaining gaps

- `debug_config/ml_tabular.toml` has no `required_dataset_type`, which `write_debug_config` requires (`KeyError` in `--debug`).
- The synthetic debug connector must produce labels (`n_classes >= 2`) for training.
- No entry in `clinnova_fl/cli.py` and no console script in `pyproject.toml` (hyphenated name, e.g. `clinnova-ml-tabular`).
