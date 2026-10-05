# `dataset` module — quickstart

High-level dataset objects used by app client code.
**Apps must only use this module**, never `data_connector` directly.
A dataset wraps a data connector and exposes a uniform, type-specific API (`__getitem__`, `__len__`, `get_feature`, `labels`).

## Structure

| File | Purpose | Page |
|------|---------|------|
| `__init__.py` | `EXISTING_DATASTE_TYPE = ["images", "tabular"]` (sic). | [`__init__.md`](./__init__.md) |
| `generic.py` | ABC `dataset`, factory `get_dataset`, `get_dataset_class`. | [`generic.md`](./generic.md) |
| `tabular.py` | Tabular (tidy data: rows = samples, columns = features) dataset. Returns numpy or torch. | [`tabular.md`](./tabular.md) |
| `images.py` | Image dataset stub (not implemented). | [`images.md`](./images.md) |
| `README.md` | One line. | — |

## How a dataset is created (client side)

```python
# in apps/client.py
dataset_istance = clinnova_fl.dataset.generic.get_dataset(custom_config, node_config)
```
1. `dataset_id = custom_config['dataset_id']`.
2. `node_config[dataset_id]` → `dataset_connector_config_file_path`, `dataset_types`.
3. Load the connector TOML → `config.connector.generic.get_connector_config` → `data_connector.generic.get_connector`.
4. `get_dataset_class(dataset_types)(dataset_id = ..., data_connector = ...)`.

Example node config (per client) :
```toml
[my_dataset]
dataset_types = "tabular"
dataset_connector_config_file_path = "/secure/path/my_dataset_connector.toml"
```

## Adding a dataset type

1. Create `dataset/<type>.py` with `class dataset(generic.dataset)` (the class is always named `dataset`, shadowing the base name inside the module).
2. Call `super().__init__(dataset_id, data_connector)` (or set `self.labels` yourself) and implement `get_feature` (abstract).
3. Add `<type>` to `EXISTING_DATASTE_TYPE` and a branch to `generic.get_dataset_class`.

## Known issues (module level)

- `tabular.py`/`images.py` import `torch`, which is not a declared dependency in `pyproject.toml`. Importing `dataset.tabular` fails without torch.
- Labels from the connector are never propagated to the dataset (see [`tabular.md`](./tabular.md)).
- `src/README.md` says `image`, the code says `images`.
