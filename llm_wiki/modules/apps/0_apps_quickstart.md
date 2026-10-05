# `apps` module — quickstart

The `apps` module contains the Flower applications.
It is the core of the package from the researcher's point of view.

## Structure

```txt
apps/
├── __init__.py            # LIST_OF_APPS
├── client.py              # ROOT ClientApp: dispatches query/train/evaluate to the specific app
├── server.py              # ROOT ServerApp: loads config, builds experiment_config, dispatches to the specific app
├── support_fl.py          # Server-side helpers: wait for nodes, send/receive Messages with retries
├── flower_hist/           # Federated histogram (2 QUERY rounds, custom strategy)
└── flower_ml_tabular/     # Classic ML on tabular data via Flower FedAvg (WIP)
```

| File | Page |
|------|------|
| `__init__.py` | [`__init__.md`](./__init__.md) |
| `client.py` | [`client.md`](./client.md) |
| `server.py` | [`server.md`](./server.md) |
| `support_fl.py` | [`support_fl.md`](./support_fl.md) |
| `flower_hist/` | [`flower_hist/0_flower_hist_quickstart.md`](./flower_hist/0_flower_hist_quickstart.md) |
| `flower_ml_tabular/` | [`flower_ml_tabular/0_flower_ml_tabular_quickstart.md`](./flower_ml_tabular/0_flower_ml_tabular_quickstart.md) |

## Dispatch model

Only the root app is a real Flower app (`pyproject.toml` → `serverapp = "clinnova_fl.apps.server:app"`, `clientapp = "clinnova_fl.apps.client:app"`).
The specific app is selected at runtime by `context.run_config["app"]`.

Server side :
```python
# Specific app server.py
def main(grid : Grid, context : Context, experiment_config : dict) -> None : ...
```

Client side :
```python
# Specific app client.py (implement only those you need)
def query(msg : Message, context : Context, dataset_istance) -> Message : ...
def train(msg : Message, context : Context, dataset_istance) -> Message : ...
def evaluate(msg : Message, context : Context, dataset_istance) -> Message : ...
```

The root client builds `dataset_istance` (note the spelling used everywhere in the code) before dispatching, so the specific app never touches `data_connector` directly.

## How to add a new app (checklist)

1. Create `apps/<app_name>/` with `__init__.py`, `server.py`, `client.py` (optionally `cli.py`, `README.md`).
2. Implement `server.main(grid, context, experiment_config)`.
    - Read app settings from `experiment_config['app_config']`.
    - Either use a Flower strategy (e.g. `flwr.serverapp.strategy.FedAvg().start(...)`, see `flower_ml_tabular`) or a custom loop with `support_fl.get_node_ids` + `support_fl.get_data_from_clients` (see `flower_hist`).
    - When using the custom loop, include `dataset_id` (and in simulation `simulation` + `paths_nodes_config`) in the `custom_config` sent to clients, because the root client reads them from there. Forwarding a copy of `app_config` does this automatically.
3. Implement the client functions with the extra `dataset_istance` argument. Return `Message(content, reply_to = msg)`.
4. Register the app :
    - add the name to `LIST_OF_APPS` in `apps/__init__.py`;
    - add a branch in `apps/server.py:return_server_module`;
    - add branches in `apps/client.py` for each of `query`, `train`, `evaluate` (raise `NotImplementedError` for unused ones).
5. Optionally add a debug template in `config/debug_config/` and register it in `config/__init__.py:DEBUG_CONFIG_PATH`, then a console script in `pyproject.toml` + a function in `clinnova_fl/cli.py`.
6. Use the **same app name string** in all of the above (currently the names are inconsistent for the ML app, see below).

## Known issues (module level)

- App name mismatch for the ML app: `LIST_OF_APPS` and `client.py` use `"flower_ml"`, `server.py:return_server_module` uses `"flower_ml_tabular"`, the debug template uses `app = "flower_ml_tabular"`. As a result the ML app cannot currently be dispatched on both sides.
- `"flower_k_means"` is listed but no `apps/flower_k_means/` package exists. The client branches just `pass`, which leads to `UnboundLocalError`/`NameError` on the later call.
- `return_server_module` has no `else` branch, so an unknown name raises `UnboundLocalError` (masked by the earlier `LIST_OF_APPS` check).
