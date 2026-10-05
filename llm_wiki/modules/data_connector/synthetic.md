# `clinnova_fl/data_connector/synthetic.py`

Generates random data for tests and debug federations (used by `clinnova-hist --debug`).

## `class data_connector(generic.data_connector)`

- `__init__(config : synthetic_connector_config)` (does not call `super().__init__`, so `self.modality` is not set) :
    - `np.random.seed(config.seed)` (global seed);
    - `self.data = np.random.normal(loc, scale, size)` or `np.random.uniform(low, high, size)`;
    - if `size` is 2D: `self.features = ["feature_1", ..., "feature_n"]`, else `None`;
    - `set_labels()`.
- `__getitem__(idx)`: `self.data[idx]` (numpy indexing).
- `__len__()`: `self.data.shape[0]`.
- `set_labels()`: `None` if `num_classes` is `None` or `< 2` (e.g. the default `-1`); `ValueError` if it is not an int (bools rejected); random integer labels in `[0, num_classes)` if `>= 2`.
- `get_feature(name)`: column `self.features.index(name)` of `self.data`.
- `get_filtered_keys(...)`: validates the feature name and then calls `compare_numerical_features`.

## Notes

- `np.random.seed` is global and the seed is the same on every client. In debug mode only `loc` differs between clients (set by `write_debug_config`), so the noise is identical.
- `clinnova-hist --debug` works end to end with this connector (verified with flwr 1.39, Python 3.12).
