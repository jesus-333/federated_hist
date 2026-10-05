# Wiki quickstart

This file gives a compact overview of the `clinnova_fl` package: what it is, how it is structured, and how a run flows through it.
Read this first, then use [`0_wiki_index.md`](./0_wiki_index.md) to jump to the detailed pages.

## Purpose

`clinnova_fl` is a Python package, developed for the Clinnova project (LCSB, University of Luxembourg), that lets data scientists and researchers implement Federated Learning (FL) / federated analytics workflows on biological data.
It is built on top of [Flower](https://flower.ai/) (`flwr>=1.28`) and can, in principle, be executed on top of NVFlare (Flower apps running through NVFlare infrastructure).

Design philosophy (see `src/README.md`, owned by the user and not to be modified except for typos/formatting) :
- Hide the Flower plumbing from the researcher. The researcher writes app logic (client + server functions) and uses high-level dataset objects.
- Separate *raw data access* (`data_connector`) from the *dataset abstraction* used by apps (`dataset`). Apps must only use `dataset`.
- Keep the `flwr run` command lean. Almost all configuration lives in TOML files referenced by path.
- Only centralized FL (a server orchestrating clients). Decentralized FL is out of scope.

The repository is a prototype / work in progress. Several code paths are incomplete or broken (see the *Known issues* sections in each page and the consolidated list in [`0_wiki_index.md`](./0_wiki_index.md#known-issues-consolidated)).

## Repository layout (relevant parts)

```txt
federated_hist/
├── pyproject.toml         # Package metadata + Flower app definition (root ServerApp/ClientApp)
├── README.md              # Repo-level notes on run_config and launching (WIP)
├── data/                  # Small datasets (PRISM IBD metagenomics data, CSV/XLSX)
├── examples/              # Example Flower projects using the package (fed_hist_1)
├── llm_wiki/              # This wiki
└── src/
    ├── README.md          # Package philosophy (user-owned, do not modify)
    └── clinnova_fl/
        ├── __init__.py
        ├── cli.py         # Console entry points (clinnova-hist) + debug config generator
        ├── apps/          # Flower apps: root dispatcher + specific apps (flower_hist, flower_ml_tabular)
        ├── config/        # Config dataclasses for connectors/apps + debug config templates
        ├── data_connector/# Raw data access (csv, synthetic)
        ├── dataset/       # High-level dataset objects used by apps (tabular, images)
        └── ui/            # UI (only legacy Streamlit code for now)
```

Folders `config/` (root level), `shared_app/`, `old_code_backup/` are development artefacts and are ignored by this wiki.

## Architecture in one picture

```txt
flwr run . --run-config "app='flower_hist' path_app_config='cfg.toml'"
   │
   ▼
[SERVER] clinnova_fl.apps.server:app  (@app.main)
   ├─ reads run_config (app, path_app_config, simulation, ...)
   ├─ loads app TOML  -> app_config  (must contain dataset_id)
   ├─ builds experiment_config = {app, app_config, dataset_id, simulation}
   └─ dispatches to clinnova_fl.apps.<app>.server.main(grid, context, experiment_config)
            │  sends Messages (QUERY / TRAIN / EVALUATE) with custom_config / train config
            ▼
[CLIENT] clinnova_fl.apps.client:app  (@app.query / @app.train / @app.evaluate)
   ├─ extracts custom_config from the message and builds node_config
   │     (simulation: from custom_config['paths_nodes_config'][partition-id];
   │      deployment: from context.node_config['full_node_config_path'])
   ├─ dataset.generic.get_dataset(custom_config, node_config)
   │     node_config[dataset_id] -> {dataset_types, dataset_connector_config_file_path}
   │     -> config.connector.generic.get_connector_config(toml)    (config dataclass)
   │     -> data_connector.generic.get_connector(config)           (raw data access)
   │     -> dataset.<type>.dataset(dataset_id, data_connector)     (high-level object)
   └─ dispatches to clinnova_fl.apps.<app>.client.<query|train|evaluate>(msg, context, dataset)
```

## Key concepts

- **Root app**: `apps/server.py` and `apps/client.py` are the only "true" Flower apps (registered in `pyproject.toml` under `[tool.flwr.app.components]`). They dispatch to specific apps by the `app` key in `run_config`.
- **Specific app**: a sub-folder of `apps/` with `client.py` and `server.py` (and optionally `cli.py`). Server entry point signature: `main(grid, context, experiment_config)`. Client entry points: `query/train/evaluate(msg, context, dataset_istance)`.
- **`run_config`**: Flower run configuration. Only keys already declared in `[tool.flwr.app.config]` of `pyproject.toml` can be overridden: `app`, `path_app_config`, `dataset_id`, `simulation`, `run_with_nvflare`.
- **`experiment_config`**: dict built by the root server: `{app, app_config, dataset_id, simulation}`.
- **`custom_config`**: dict sent from server to clients inside `msg.content.config_records["custom_config"]` (see `apps/support_fl.py`). Only Flower `ConfigRecord`-compatible types are allowed (scalars, str, bytes, bool and flat lists of those).
- **`node_config`**: per-client mapping `dataset_id -> {dataset_types, dataset_connector_config_file_path}`. Tells each client where its local data is and what type it is.
- **Data connector config**: TOML file (per client, per dataset) with a `modality` key (`csv` or `synthetic`) and modality-specific options.

## Getting started

Install (Python >= 3.12 is effectively required, because some f-strings reuse the same quote type inside replacement fields) :
```sh
pip install -e .
```

Run the histogram app in debug mode (synthetic data, 7 simulated supernodes, configs generated in `./debug/`) :
```sh
clinnova-hist --debug
```

Run with a custom app config in simulation :
```sh
clinnova-hist --config_file path/to/hist.toml --simulation
```

Equivalent raw Flower command (run from the repo root) :
```sh
flwr run . --federation @none/default --stream \
  --run-config "simulation='true'" \
  --run-config "app='flower_hist' path_app_config='path/to/hist.toml'"
```

Note that, with `flwr>=1.28`, federations are configured in `~/.flwr/config.toml`, not in `pyproject.toml`.

## Where to go next

- Adding a new FL app: [`modules/apps/0_apps_quickstart.md`](./modules/apps/0_apps_quickstart.md).
- Adding a new data source: [`modules/data_connector/0_data_connector_quickstart.md`](./modules/data_connector/0_data_connector_quickstart.md) and [`modules/config/0_config_quickstart.md`](./modules/config/0_config_quickstart.md).
- Adding a new dataset type: [`modules/dataset/0_dataset_quickstart.md`](./modules/dataset/0_dataset_quickstart.md).
- Coding conventions: [`coding_style_instructions_ENG.md`](./coding_style_instructions_ENG.md) (mandatory, do not modify).
