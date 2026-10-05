# `clinnova_fl/data_connector/synthetic.py`

Generates random data for tests and debug federations (used by `clinnova-hist --debug`).

## `class data_connector(generic.data_connector)`

- `__init__(config : synthetic_connector_config)` (does not call `super().__init__`, so `self.modality` is not set) :
    - `np.random.seed(config.seed)` (global seed);
    - `self.data = np.random.normal(loc, scale, size)` or `np.random.uniform(low, high, size)`;
    - if `size` is 2D: `self.features = ["feature_1", ..., "feature_n"]`, else `None`;
    - `set_labels()`.
- `__getitem__(idx)`: `self.data[idx].to_numpy()`.
- `__len__()`: `self.data.shape[0]`.
- `set_labels()`: random integer labels in `[0, num_classes)` if `num_classes >= 2`, else `None`.
- `get_feature(name)`: column `self.features.index(name)` of `self.data`.
- `get_filtered_keys(...)`: validates the feature name and then calls `compare_numerical_features`.

## Known issues (blocking for `--debug`)

1. `set_labels` reads `self.config.num_classes`, but the config field is `n_classes` → `AttributeError`.
2. The type check is inverted: `if type(num_classes) is int : raise ValueError(...)`.
3. With `n_classes = -1` (template default) the intended behaviour is "no labels", but the code raises for values `< 2` instead of setting `None`. Only `None` disables labels.
4. `__getitem__` calls `.to_numpy()` on a numpy array → `AttributeError`. Return `self.data[idx]` directly.
5. Feature names start at `feature_1`, but the hist debug template uses `feature_0`.
6. `np.random.seed` with the same seed on every client: only `loc` differs between debug clients (set by `write_debug_config`), the noise is identical.
