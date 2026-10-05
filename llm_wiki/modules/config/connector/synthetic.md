# `clinnova_fl/config/connector/synthetic.py`

## `@dataclass class synthetic_connector_config(connector_config)`

| Field | Default | Notes |
|-------|---------|-------|
| `modality` | `'synthetic'` | |
| `seed` | `42` | |
| `distribution` | `'normal'` | `'normal'` or `'uniform'`. |
| `size` | `(1000, 20)` | `(n_samples, n_features)` for tabular data. |
| `num_classes` | `-1` | `>= 2` to generate labels. `None` or `< 2` means no labels. |
| `loc`, `scale` | `0`, `1` | Normal distribution. |
| `low`, `high` | `0`, `1` | Uniform distribution. |

- `to_dict()`: sets to `None` the parameters of the distribution that is not selected.
- `from_dict(d)`: `d.get(...)` with defaults. The default for `num_classes` is `-1` (no labels), the same as the dataclass default.

No validation in `__post_init__` (e.g. distribution, `num_classes`).

## Consumer

`data_connector/synthetic.py` (see [`../../data_connector/synthetic.md`](../../data_connector/synthetic.md)).
The connector reads `config.num_classes`.
