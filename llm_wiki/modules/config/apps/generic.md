# `clinnova_fl/config/apps/generic.py`

Skeleton for typed app configurations. **Not used** anywhere yet: apps currently receive a plain dict (`experiment_config['app_config']`).

- `IMPLEMENTED_APP = ['flower_hist']`.
- `@dataclass class app_config(ABC)`: same structure as `connector/generic.py:connector_config` (copied, docstrings still talk about connectors): `modality` attribute, `__post_init__`, abstract `to_dict`, abstract classmethod `from_dict`, concrete classmethod `from_toml`.
- `get_app_config(connector_config_dict)`: empty stub (docstring only, returns `None`).

Intended direction (from `src/README.md`: "`experiment_config` ... a dictionary or a dataclass"): one dataclass per app with validation in `__post_init__`, built from the app TOML.
