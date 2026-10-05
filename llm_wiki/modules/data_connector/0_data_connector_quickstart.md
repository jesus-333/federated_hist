# `data_connector` module — quickstart

Raw data access layer.
A connector reads data from a specific source (CSV file, synthetic generator, in future DBs/APIs) and returns numpy data.
It is used only internally by `dataset`.
Each connector is configured by a dataclass from `config/connector/` (selected by its `modality`).

## Structure

| File | Purpose | Page |
|------|---------|------|
| `__init__.py` | Docstring only. | — |
| `generic.py` | ABC `data_connector`, shared filtering helpers, factory `get_connector`. | [`generic.md`](./generic.md) |
| `csv.py` | CSV connector (pandas). | [`csv.md`](./csv.md) |
| `synthetic.py` | Random normal/uniform data for testing/debugging. | [`synthetic.md`](./synthetic.md) |

## Contract (abstract methods)

```python
__getitem__(key)                 # sample(s)
__len__() -> int
set_labels()                     # set self.labels (or None); called at the end of __init__
get_feature(feature : str)       # 1D array of one feature
get_filtered_keys(feature, comparison_type, filter_value)  # keys satisfying a condition
```
Inherited: `get_sample(key)`, `compare_numerical_features(...)`, `filter_based_on_feature_value(...)`.

## Adding a connector

1. Config dataclass in `config/connector/<modality>.py` (see [`../config/0_config_quickstart.md`](../config/0_config_quickstart.md)).
2. `data_connector/<modality>.py` with `class data_connector(generic.data_connector)` (the class is always named `data_connector`).
3. Implement all abstract methods. Load the data **before** `set_labels()` runs (the base `__init__` calls `set_labels()`, so either load data first and then call `super().__init__`, or do not call it and set `modality`/`config` yourself).
4. Add a branch to `generic.get_connector` and to `config.connector.generic.get_connector_config`.

## Known issues (module level)

Neither of the two connectors currently works end-to-end (see their pages).
