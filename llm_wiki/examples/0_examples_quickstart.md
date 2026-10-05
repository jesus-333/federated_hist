# Examples — quickstart

Description of the content of the repository `examples/` folder.
Each example is a self-contained Flower project (its own `pyproject.toml`) that imports the installed `clinnova_fl` package.
So `flwr run .` can be executed from the example folder instead of the repository root.

| Example | Description | Page |
|---------|-------------|------|
| `fed_hist_1/` | Minimal Flower project that re-exports the root `clinnova_fl` ServerApp/ClientApp, intended for the histogram app. | [`fed_hist_1.md`](./fed_hist_1.md) |

Pattern for a new example :
1. `examples/<name>/app.py` re-exporting `clinnova_fl.apps.server.app` and `clinnova_fl.apps.client.app`.
2. `examples/<name>/pyproject.toml` with `[tool.flwr.app.components]` pointing to them and the same `[tool.flwr.app.config]` keys as the root `pyproject.toml` (`app`, `path_app_config`, `dataset_id`, `simulation`, `run_with_nvflare`). Keys not declared there cannot be overridden by `--run-config`.
3. App config TOML and, for deployment, node/connector configs on each client.
