# `clinnova_fl/dataset/tabular.py`

Tabular dataset in tidy format (rows = samples, columns = features).

## `class dataset(generic.dataset)`

### `__init__(dataset_id, data_connector, return_type = 'numpy')`

- `SUPPORTED_RETURN_TYPES = ['numpy', 'torch']` (instance attribute).
- Stores `dataset_id`, `data_connector`, `return_type`.
- Does **not** call `super().__init__` and does **not** set `self.labels`.

### `__getitem__(row_idx)`

`sample = data_connector[row_idx]`, `label = self.labels[row_idx]` (if not `None`).
Both are converted to `np.array` or `torch.tensor`.
Returns `sample` or `(sample, label)`.

### `get_feature(feature_name)`

`data_connector.get_feature(feature_name)` converted to numpy/torch.
A connector `NotImplementedError` is re-raised with a clearer message.
Used by `flower_hist`.

### `show_supported_return_types()`

Prints the supported return types.

## Known issues

- `self.labels` is never assigned, so `__getitem__` and `flower_ml_tabular.client.train` raise `AttributeError`. The connector exposes `data_connector.labels`. The fix is to call `super().__init__(...)` and set `self.labels = getattr(data_connector, 'labels', None)`.
- `torch` is imported at module level (a hard dependency even for numpy users), but it is not in `pyproject.toml`.
- `return_type` cannot be set from configuration (always the default `'numpy'` via `get_dataset`).
