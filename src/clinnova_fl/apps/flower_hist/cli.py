"""
Implements the command-line logic for the hist app

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

import subprocess
import sys
import toml

from pathlib import Path

from clinnova_fl.cli import write_debug_config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main_hist(args, flwr_args) -> None:
    """
    Run the histogram Flower app through `flwr run`.
    """

    # ***************************************
    # Check if arguments are passed

    if args.debug :
        path_server_config = write_debug_config("flower_hist")
        print(f"Debug mode enabled. A copy of the config used is saved at : {path_server_config}")
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
