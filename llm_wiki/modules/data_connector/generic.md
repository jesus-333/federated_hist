# `clinnova_fl/data_connector/generic.py`

## `class data_connector(ABC)`

- Class attribute `SUPPORTED_COMPARISON_TYPE = ['equals', 'not_equals', 'greater_than', 'less_than', 'less_than_or_equal', 'greater_than_or_equal']`.
- `__init__(config)`: `self.modality = config.modality`, `self.config = config`, then `self.set_labels()`.
- Abstract methods: `__getitem__`, `__len__`, `set_labels`, `get_feature`, `get_filtered_keys`.
- `get_sample(key)`: alias of `__getitem__`.
- `compare_numerical_features(feature, comparison_type, filter_value, return_int_idx = False)`: applies the comparison on `np.asarray(self.get_feature(feature))`. Returns a boolean mask, or integer indices if `return_int_idx`.
- `filter_based_on_feature_value(feature, comparison_type, filter_value)`: `keys = get_filtered_keys(...)`, checks that they are non-empty and iterable, then returns `self[keys]`. On failure it raises a detailed `ValueError`.

## `get_connector(connector_config) -> data_connector`

Dispatches on `connector_config.modality`: `'csv'` → `data_connector.csv.data_connector`, `'synthetic'` → `data_connector.synthetic.data_connector`.
The error message references `generic.SUPPORTED_COMPARISON_TYPE` on the config module, which does not exist (`AttributeError` when the error path is hit). It should be `SUPPORTED_MODALITY`.

## Notes

- `get_filtered_keys` has no body (only a docstring), so calling `super().get_filtered_keys` returns `None`.
- Filtering is not wired to any config option yet.
