# `clinnova_fl/config/connector/csv.py`

Marked **"TO REWRITE"** in its docstring. It currently cannot be imported.

## Intended content

- `SUPPORTED_FILTER_TYPES = {'equals', 'less_than', 'greater_than', 'less_than_or_equal_to', 'greater_than_or_equal_to'}`.
- `@dataclass class csv_connector_config` with fields :
    - `modality = 'csv'`;
    - `file_path : str | Path` (converted to `Path`);
    - `field_name : str` (single column to extract);
    - optional `filter_field`, `filter_type`, `filter_value`. If `filter_field` is set, the other two are required and `filter_type` must be supported. Otherwise they are reset to `None` with a warning print.
- `to_dict()`, `from_dict()`.

## Known issues (blocking)

1. Imports `generic_connector_config` from `config.connector.generic`, which defines `connector_config` → `ImportError`.
2. Non-default fields (`file_path`, `field_name`) follow the defaulted `modality` → dataclass `TypeError`.
3. Field mismatch with `data_connector/csv.py`: the connector reads `config.feature_to_predict`, which is not a field here. `field_name` and filter options are not used by the connector.
4. Filter names differ from `data_connector.generic.SUPPORTED_COMPARISON_TYPE` (`less_than_or_equal` vs `less_than_or_equal_to`, and there is no `not_equals` here).
5. `from_dict` does not forward `modality`.

When rewriting, align the fields with what `data_connector/csv.py` needs: `file_path`, optional `feature_to_predict`, optional sample-id handling, and optional row filtering.
