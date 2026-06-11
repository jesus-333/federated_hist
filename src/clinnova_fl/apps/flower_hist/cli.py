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

    num_supernodes = 7

    if args.debug :
        path_app_config = write_debug_config(num_supernodes, "flower_hist",)
        print(f"Debug mode enabled. A copy of the config used is saved at : {path_app_config}")
    elif args.config_file is None :
        path_app_config = "./config/hist.toml"
        print(f"No configuration file provided. Using the default one: {path_app_config}")
    else :
        path_app_config = args.config_file
    
    # Check if arguments are valid
    if not Path(path_app_config).is_file() : # Check if the provided configuration file exists
        print(f"Error: The provided configuration file does not exist: {path_app_config}")
        sys.exit(1)
    if Path(path_app_config).suffix != ".toml" : # Check if the provided configuration file is a toml file
        print(f"Error: The provided configuration file is not a toml file: {path_app_config}")
        sys.exit(1)

    # ***************************************
    # Check if the provided configuration file is valid
    
    config = toml.load(path_app_config)

    if 'app' not in config or config['app'] != 'flower_hist' :
        print(f"Error: The provided configuration file does not contain a valid 'app = \"flower_hist\"' entry: {path_app_config}")
        sys.exit(1)
    # if 'flower_hist_config' not in config :
    #     print(f"Error: The provided configuration file does not contain the 'flower_hist_config' section: {path_app_config}")
    #     sys.exit(1)

    # ***************************************

    command = ["flwr", "run", "."]

    if args.simulation or args.debug :
        # Add custom flag for simulation/debug
        command += ["--federation", "@none/default", "--stream", "--run-config", "simulation='true'"]

        # In case of debug add also the number of supernodes
        if args.debug : command += ["--federation-config", f"num-supernodes={num_supernodes}"]

    command += ["--run-config", f"app='flower_hist' path_app_config='{path_app_config}'"]
    # command += ["--run-config", f"{path_app_config}"]
    command += flwr_args
    
    if args.debug : print(f"Running command: {' '.join(command)}")
    
    # Execute the command ang get the return code
    code_execution = subprocess.run(command, check = False).returncode

    raise SystemExit(code_execution)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
