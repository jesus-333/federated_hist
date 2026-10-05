# `clinnova_fl/config/connector/synthetic.py`

## `@dataclass class synthetic_connector_config(connector_config)`

| Field | Default | Notes |
|-------|---------|-------|
| `modality` | `'synthetic'` | |
| `seed` | `42` | |
| `distribution` | `'normal'` | `'normal'` or `'uniform'`. |
| `size` | `(1000, 20)` | `(n_samples, n_features)` for tabular data. |
| `n_classes` | `-1` | `>= 2` to generate labels. |
| `loc`, `scale` | `0`, `1` | Normal distribution. |
| `low`, `high` | `0`, `1` | Uniform distribution. |

- `to_dict()`: sets to `None` the parameters of the distribution that is not selected.
- `from_dict(d)`: `d.get(...)` with defaults. Note that the default for `n_classes` here is `2`, while the dataclass default is `-1`.

No validation in `__post_init__` (e.g. distribution, `n_classes`).

## Consumer

`data_connector/synthetic.py` (see [`../../data_connector/synthetic.md`](../../data_connector/synthetic.md)).
The connector reads `config.num_classes`, which does **not** exist here (the field is `n_classes`).
