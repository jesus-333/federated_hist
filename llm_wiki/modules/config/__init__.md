# `clinnova_fl/config/__init__.py`

Defines `DEBUG_CONFIG_PATH`, a dict mapping names to debug template paths (absolute, resolved from the package location) :

| Key | Path | Exists |
|-----|------|--------|
| `flower_hist` | `debug_config/hist.toml` | yes |
| `flower_ml` | `debug_config/ml.toml` | **no** (actual file: `ml_tabular.toml`) |
| `synthetic` | `debug_config/synthetic_data_connector.toml` | yes |

Used by `config/config.py:get_debug_config_app` and `get_debug_config_data_connector`, called by `clinnova_fl.cli.write_debug_config`.

When adding an app or a connector with a debug template, register it here using the same key used as `app_name` / modality.
