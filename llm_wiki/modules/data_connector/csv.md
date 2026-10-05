# `clinnova_fl/data_connector/csv.py`

## `class data_connector(generic.data_connector)`

Intended behaviour :
- `__init__(config : csv_connector_config)` :
    - `pd.read_csv(config.file_path, header = 0)`, kept in memory as `self.data` (a comment flags this as a security concern for the future);
    - if the first column is named `id` or `sample_id` (case insensitive), it is moved to `self.sample_ids`;
    - all remaining columns must be numeric, otherwise `ValueError`;
    - `set_labels()`.
- `__getitem__(idx)`: `self.data.iloc[idx].to_numpy()` (int, list, slice).
- `set_labels()`: if `config.feature_to_predict` is set, label-encode that column (`astype('category').cat.codes`), reject `-1` (NaN), and drop the column from `self.data`.
- `get_feature(name)`: `self.data[name].to_numpy()`.
- `get_filtered_keys(feature, comparison_type, filter_value)`: validates the column and then returns the **boolean mask** from `compare_numerical_features` (usable with `iloc`).

## Expected data layout

Tidy CSV: header row = feature names, one row per sample, optional first id column, only numeric values.
The label column must be numeric too, because the numeric check happens before the label extraction.

The repo file `data/original_data.csv` (PRISM IBD metagenomics, Franzosa et al. 2018) is **transposed** (features as rows, samples as columns) and contains non-numeric fields (`Diagnosis`, sample names).
It must be transposed and cleaned before being used with this connector.

## Known issues (blocking)

1. No `__len__` → abstract class, cannot be instantiated.
2. `super().__init__(config)` calls `set_labels()` before `self.data` exists → `AttributeError`.
3. `config.feature_to_predict` is not a field of `csv_connector_config` (which is itself not importable, see [`../config/connector/csv.md`](../config/connector/csv.md)).
4. `np.issubdtype(self.data.dtypes.values, np.number)` is called on an array of dtypes. Use `pd.api.types.is_numeric_dtype` per column, or `self.data.select_dtypes(exclude = 'number')`.
5. Non-numeric label columns (e.g. `Diagnosis`) are rejected by the numeric check, although `set_labels` is designed to encode them.
