# `apps/flower_hist/cli.py`

## `main_hist(args, flwr_args) -> None`

Called by `clinnova_fl.cli.flower_hist`.
Builds and runs a `flwr run .` subprocess, then exits with its return code (`raise SystemExit(code)`).

Steps :
1. `num_supernodes = 7` (hard-coded).
2. Select the config path :
    - `--debug` → `write_debug_config(7, "flower_hist")` (generates `./debug/...`);
    - no `--config_file` → `./config/hist.toml` (repo-root `config/` folder, development artefact);
    - else `args.config_file`.
3. Validate: file exists, `.toml` suffix, and contains `app = "flower_hist"`. On failure it prints and calls `sys.exit(1)`.
4. Build the command :
    ```txt
    flwr run .
      [--federation @none/default --stream --run-config "simulation='true'"]   # if --simulation or --debug
      [--federation-config "num-supernodes=7"]                                 # if --debug
      --run-config "app='flower_hist' path_app_config='<path>'"
      <flwr_args...>
    ```
5. `subprocess.run(command, check = False)`.

## Notes

- `flwr run .` uses the `pyproject.toml` of the **current working directory**, so the command must be executed from the repo root (or from a Flower project such as `examples/fed_hist_1/`).
- The config path is passed as-is. Relative paths are resolved by the ServerApp process, not by the CLI.
