# `config` module — quickstart

Configuration objects and templates.
The `src/README.md` section on this module is still empty, so this wiki is the reference for it.

## Structure

```txt
config/
├── __init__.py            # DEBUG_CONFIG_PATH (paths to debug templates)
├── config.py              # Project path helpers + debug template loaders
├── README.md              # empty
├── apps/
│   ├── __init__.py        # empty
│   └── generic.py         # ABC app_config (dataclass) — skeleton, unused
├── connector/
│   ├── __init__.py        # empty
│   ├── generic.py         # ABC connector_config + factory get_connector_config
│   ├── csv.py             # csv_connector_config (broken, marked "TO REWRITE")
│   └── synthetic.py       # synthetic_connector_config
└── debug_config/          # TOML templates used by write_debug_config
    ├── hist.toml
    ├── hist_plot.toml
    ├── ml_tabular.toml
    └── synthetic_data_connector.toml
```

| File | Page |
|------|------|
| `__init__.py` | [`__init__.md`](./__init__.md) |
| `config.py` | [`config.md`](./config.md) |
| `apps/generic.py` | [`apps/generic.md`](./apps/generic.md) |
| `connector/generic.py` | [`connector/generic.md`](./connector/generic.md) |
| `connector/csv.py` | [`connector/csv.md`](./connector/csv.md) |
| `connector/synthetic.py` | [`connector/synthetic.md`](./connector/synthetic.md) |
| `debug_config/*.toml` | [`debug_config.md`](./debug_config.md) |

## Configuration layers (whole package)

| Layer | Where | Who reads it |
|-------|-------|--------------|
| `run_config` | `pyproject.toml [tool.flwr.app.config]` + `--run-config` | root `apps/server.py` |
| app config | TOML at `path_app_config` (server side) | root server → `experiment_config['app_config']` → specific app |
| `custom_config` | dict sent inside Messages | root `apps/client.py` + specific client |
| node config | per-client TOML: `dataset_id -> {dataset_types, dataset_connector_config_file_path}` | `dataset.generic.get_dataset` |
| connector config | per-client, per-dataset TOML with `modality` | `config.connector.generic.get_connector_config` → dataclass |

## Connector config pattern

Each data source has a `@dataclass` subclass of `connector_config` with :
- a `modality` class/default attribute (the dispatch key, e.g. `'csv'`, `'synthetic'`);
- validation in `__post_init__`;
- `to_dict()` and `@classmethod from_dict(cls, d)`;
- `from_toml(path)` inherited from the base class (loads the TOML and then calls `from_dict`).

To add a new modality: create `config/connector/<modality>.py`, add it to `SUPPORTED_MODALITY` and to `get_connector_config` in `connector/generic.py`, then create the matching connector in `data_connector/` (see [`../data_connector/0_data_connector_quickstart.md`](../data_connector/0_data_connector_quickstart.md)).
