# Example `examples/fed_hist_1/`

## Files

`app.py` :
```python
from clinnova_fl.apps import client, server

server_app = server.app
client_app = client.app
```

`pyproject.toml` :
- `[project] name = "hist-example-1"`. It has **no** `[build-system]` or dependencies, so it expects `clinnova_fl` to be already installed in the environment.
- `[tool.flwr.app.components]`: `serverapp = "app:server_app"`, `clientapp = "app:client_app"`.
- `[tool.flwr.app.config]`: `app`, `path_app_config`, `dataset_id` (placeholders `"X"`), `simulation = false`, `run_with_nvflare = false`.

## Usage

```sh
pip install -e <repo_root>
cd examples/fed_hist_1
flwr run . --federation @none/default --stream \
  --run-config "simulation='true'" \
  --run-config "app='flower_hist' path_app_config='/abs/path/hist.toml'"
```

In simulation, the app config must provide `dataset_id` and `paths_nodes_config` (one node-config TOML per partition), e.g. generated with `clinnova_fl.cli.write_debug_config`.

## Notes

- No app config, node config or data is shipped with the example yet.
- The `clinnova-hist` CLI always runs `flwr run .` in the current directory, so it can also be launched from this folder.
