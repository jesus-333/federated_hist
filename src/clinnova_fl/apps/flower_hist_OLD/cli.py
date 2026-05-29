"""
Implements the command-line logic for the hist app

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

def main_hist(args, flwr_args) -> None:
    """
    Run the histogram Flower app through `flwr run`.
    """

    # ***************************************
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
    if Path(path_server_config).suffix != ".toml" : # Check if the provided configuration file is a toml file
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

    if args.simulation :
        command += ["--federation", "@none/default", "--stream"]
    elif args.debug :
        command += ["--federation", "@none/default", "--stream", "--federation-config", "num-supernodes=7"]

    command += ["--run-config", f"app='flower_hist' path_server_config='{path_server_config}'"]
    # command += ["--run-config", f"{path_server_config}"]
    command += flwr_args
    
    if args.debug : print(f"Running command: {' '.join(command)}")
    
    # Execute the command ang get the return code
    code_execution = subprocess.run(command, check = False).returncode

    raise SystemExit(code_execution)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
