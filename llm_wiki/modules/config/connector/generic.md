# `clinnova_fl/config/connector/generic.py`

## `SUPPORTED_MODALITY`

```python
SUPPORTED_MODALITY = [
    'csv'
    'synthetic',
]
```
A comma is missing, so this evaluates to `['csvsynthetic']`. It is only used in an error message.

## `@dataclass class connector_config(ABC)`

Base class of all connector configs.
- `modality : str = None`. Must be overridden by subclasses.
- `__post_init__()`: no-op hook for validation.
- `to_dict() -> dict`: abstract.
- `from_dict(cls, config_dict) -> connector_config`: abstract classmethod.
- `from_toml(cls, toml_path) -> connector_config`: checks existence, `toml.load`, then `cls.from_dict(...)`. Raises `FileNotFoundError` or `ValueError`.

Dataclass inheritance caveat: since the base defines a defaulted field (`modality`), subclasses cannot declare non-default fields after it (`TypeError: non-default argument follows default argument`). Give every subclass field a default, or use `kw_only = True` (Python >= 3.10).

## `get_connector_config(connector_config_dict : dict)`

Factory on `connector_config_dict['modality']` :
- `'csv'` → `csv.csv_connector_config.from_dict(...)`;
- `'synthetic'` → `synthetic.synthetic_connector_config.from_dict(...)`;
- otherwise `ValueError`.

Called by `dataset.generic.get_dataset` after loading the per-dataset TOML from the node config.
