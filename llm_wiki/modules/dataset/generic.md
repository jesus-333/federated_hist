# `clinnova_fl/dataset/generic.py`

## `class dataset(ABC)`

Attributes: `dataset_id : str`, `data_connector`, `labels` (default `None`).
If `labels` is set, it must be indexable with the same keys used for the samples.

- `__init__(dataset_id, data_connector)`: stores both and sets `labels = None`.
- `__getitem__(key)`: returns `data_connector[key]`, or `(data_connector[key], labels[key])` if there are labels.
- `__len__()`: `len(data_connector)`.
- `get_feature(feature)`: abstract (all samples of one feature).

Implementing `__getitem__`/`__len__` makes datasets compatible with `torch.utils.data.DataLoader`.

## `get_dataset(experiment_config : dict, node_config : dict) -> dataset`

See [`0_dataset_quickstart.md`](./0_dataset_quickstart.md#how-a-dataset-is-created-client-side).
Despite the name, the first argument is the client's `custom_config` (it must contain `dataset_id`).
Raises `KeyError` if `dataset_id` is missing from `custom_config` or `node_config`, and `ValueError` for unsupported types.

## `get_dataset_class(dataset_type : str)`

`"tabular"` → `dataset.tabular.dataset`, `"images"` → `dataset.images.dataset`. There is no `else` branch.

## Notes

- The node config stores a path to a TOML per dataset. A comment says this may change for security reasons.
- The base `__init__` docstring is copy-pasted from the connector.
