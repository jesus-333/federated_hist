# `clinnova_fl/cli.py`

Command-line interface of the package.
Contains the top-level console entry points and the helper that generates the debug (synthetic) configuration for a simulated federation.

## Functions

### `flower_hist() -> None`

Entry point of the `clinnova-hist` console script.
- Parses with `argparse.ArgumentParser(prog = "clinnova-hist")` using `parse_known_args()`, so unknown flags are forwarded verbatim to `flwr run`.
- Arguments :
    - `--config_file` (default `None`) : path to the app TOML config.
    - `--simulation` (flag) : run in simulation mode.
    - `--debug` (flag) : simulation with auto-generated synthetic debug config.
- Lazily imports `clinnova_fl.apps.flower_hist.cli` and calls `main_hist(args, flwr_args)`.

Note: argument names use underscores (`--config_file`), while the coding style requires hyphens for multi-word CLI names (applies to new CLIs).

### `write_debug_config(n_clients : int, app_name : str) -> pathlib.Path`

Builds a full fake federation on disk under `./debug/` (relative to the CWD) :
1. Loads the app debug template via `config.get_debug_config_app(app_name)` (path from `DEBUG_CONFIG_PATH[app_name]`).
2. Adds `paths_nodes_config = ["debug/node_config_client_{i}.toml", ...]` to the app config and saves it as `debug/config_{app_name}.toml`.
3. Loads the synthetic data-connector template (`config.get_debug_config_data_connector('synthetic')`).
4. For each client `i` :
    - sets `loc = i` (different mean per client) and `size = data_size_based_on_dataset_type[required_dataset_type]` (e.g. `[500, 20]` for `tabular`);
    - saves `debug/synth_1_node_{i}.toml`;
    - writes `debug/node_config_client_{i}.toml` with two entries: `synth_1` (real, `dataset_types = required_dataset_type`) and `syth_2` (fake, illustrative only).
5. Returns the path of the generated app config.

The app debug template must contain `required_dataset_type`.
The generated app config must use `dataset_id = 'synth_1'` to match the node config.

On the client side, in simulation, `apps/client.py:get_simulated_node_config` picks `custom_config['paths_nodes_config'][partition-id]`.
This works because the server forwards the full `app_config` (including `paths_nodes_config`) as `custom_config`.

## Known issues

- Unused imports: `random`, `DEBUG_CONFIG_PATH`.
- The extra `syth_2` entry leaks the extra dataset into the node config. It is harmless but its key has a typo.
- `n_classes` stays `-1` in the generated synthetic configs, and the generated features are named `feature_1 ... feature_n` while the hist debug template asks for `bins_variable = "feature_0"`. Together with the bugs in the synthetic connector, `clinnova-hist --debug` currently fails on the client side (see [`../data_connector/synthetic.md`](../data_connector/synthetic.md)).
