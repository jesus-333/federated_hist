# `apps/flower_hist` — quickstart

Federated histogram of one feature of a tabular dataset split among clients.
It is the reference example of an app with a **custom strategy** built on `@app.query()` messages.
The app has also its own `README.md` in the source folder.

## Files

| File | Purpose | Page |
|------|---------|------|
| `__init__.py` | Docstring only. | — |
| `README.md` | User doc: outputs and config options. | — |
| `cli.py` | `main_hist(args, flwr_args)`: builds and runs the `flwr run` command. | [`cli.md`](./cli.md) |
| `client.py` | `query(msg, context, dataset_istance)`: local min/max, then local histogram. | [`client.md`](./client.md) |
| `server.py` | `main(grid, context, experiment_config)`: 2-round protocol + saving. | [`server.md`](./server.md) |
| `support.py` | Plot helpers (unfinished). | [`support.md`](./support.md) |

## Protocol

```txt
Round 0 (skipped if predefined_min AND predefined_max are given)
  server --QUERY custom_config{..., server_round=0}--> clients
  clients: min/max of dataset.get_feature(bins_variable)
  server: global min = min(mins), global max = max(maxs)
Round 1
  server: bins = linspace/geomspace(min, max, n_bins + 1)
  server --QUERY custom_config{..., server_round=1, bins=[...]}--> clients
  clients: np.histogram(feature, bins), mean, std
  server: sum histograms, weighted mean/std, save results
```

## App config (TOML referenced by `path_app_config`)

| Key | Default | Notes |
|-----|---------|-------|
| `app` | — | Must be `"flower_hist"` (checked by `cli.py`). |
| `dataset_id` | — | Required by root server. Must exist in each client's `node_config`. |
| `bins_variable` | — (required) | Feature name. If it contains `:` (e.g. `"1.1.1.1: Alcohol dehydrogenase"`), the part after `:` is used for output folder/file names. |
| `n_bins` | `10` | |
| `bins_distribution` | `'uniform'` | `'uniform'` or `'logarithmic'`. |
| `predefined_min`, `predefined_max` | `None` | Optional. Overrides the computed value. |
| `min_nodes` | `1` | Minimum connected nodes to start. |
| `max_number_of_attempts` | `10` | Retries for send/receive. |
| `path_to_save` | `'./results/'` | Server side. |
| `create_plot` | — | Documented but not implemented. |
| `paths_nodes_config` | — | Simulation only. Added by `write_debug_config`. |

Debug template: `config/debug_config/hist.toml`.

## Outputs

In `{path_to_save}/{bins_variable_name}/` (relative to the SuperLink/ServerApp working directory) :
- `results_{name}.pkl` and `results_{name}.toml`: the forwarded config plus `bins`, `histogram`, `mean`, `std`;
- `bins_{name}.npy`, `hist_{name}.npy`.

The source `README.md` names the files `*_{bins_distribution}.*`, but the code uses the bins variable name.

## Run

```sh
clinnova-hist --config_file my_hist.toml --simulation
clinnova-hist --debug
```
