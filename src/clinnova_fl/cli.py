"""
Implements the command-line interface for the clinnova_fl package.

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

import argparse
import random
import subprocess
import sys
import toml

from pathlib import Path

from clinnova_fl import DEBUG_CONFIG_PATH

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def _write_debug_config(app_name : str) -> Path:
    """
    Create the temporary debug config used by the histogram app.
    """

    template_path = DEBUG_CONFIG_PATH[app_name]

    debug_dir = Path("debug")
    debug_dir.mkdir(parents = True, exist_ok = True)

    debug_config = toml.load(template_path)
    debug_config["flower_hist_config"]["seed"] = random.randint(0, 2**31 - 1)

    path_debug_config = debug_dir / "config_hist.toml"
    with path_debug_config.open("w", encoding = "utf-8") as f:
        toml.dump(debug_config, f)

    return path_debug_config

def main_hist() -> None:
    """
    Run the histogram Flower app through `flwr run`.
    """

    # ***************************************
    # Command-line arguments parsing
    
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(prog = "clinnova-hist")
    parser.add_argument("--config_file", default = None, help = "Path to the histogram server configuration file.",)
    parser.add_argument("--simulation" , default = False, action = "store_true", help = "Run the histogram app in simulation mode.")
    parser.add_argument("--debug"      , default = False, action = "store_true", help = "Run the histogram app in simulation mode with the debug federation settings.")
    args, flwr_args = parser.parse_known_args()

    # Check if arguments are passed
    if args.debug :
        path_server_config = _write_debug_config("flower_hist")
        print(f"Debug mode enabled. Using temporary configuration file: {path_server_config}")
    elif args.config_file is None :
        path_server_config = "./config/hist.toml"
        print(f"No configuration file provided. Using the default one: {path_server_config}")
    else :
        path_server_config = args.config_file

    # Check if arguments are valid
    if not Path(path_server_config).is_file() : # Check if the provided configuration file exists
        print(f"Error: The provided configuration file does not exist: {path_server_config}")
        sys.exit(1)
    if not path_server_config.endswith(".toml") : # Check if the provided configuration file is a toml file
        print(f"Error: The provided configuration file is not a toml file: {path_server_config}")
        sys.exit(1)

    # ***************************************
    # Check if the provided configuration file is valid
    
    config = toml.load(path_server_config)

    if 'app' not in config or config['app'] != 'flower_hist' :
        print(f"Error: The provided configuration file does not contain a valid 'app = \"flower_hist\"' entry: {path_server_config}")
        sys.exit(1)
    if 'flower_hist_config' not in config :
        print(f"Error: The provided configuration file does not contain the 'flower_hist_config' section: {path_server_config}")
        sys.exit(1)

    # ***************************************

    command = ["flwr", "run", "."]

    if args.simulation or args.debug:
        command += ["--federation", "local-simulation"]

    command += ["--run-config", f"path_server_config={path_server_config}"]

    command += flwr_args

    raise SystemExit(subprocess.run(command, check = False).returncode)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
