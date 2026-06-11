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

import pathlib
import random
import toml

from clinnova_fl.config import DEBUG_CONFIG_PATH, config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def flower_hist() -> None:
    """
    Run the flower hist app
    """

    # ***************************************
    # Command-line arguments parsing
    
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(prog = "clinnova-hist")
    parser.add_argument("--config_file", default = None, help = "Path to the histogram server configuration file.",)
    parser.add_argument("--simulation" , default = False, action = "store_true", help = "Run the histogram app in simulation mode.")
    parser.add_argument("--debug"      , default = False, action = "store_true", help = "Run the histogram app in simulation mode with the debug federation settings.")
    args, flwr_args = parser.parse_known_args()

    # ***************************************

    from clinnova_fl.apps.flower_hist import cli

    cli.main_hist(args, flwr_args)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def write_debug_config(n_clients : int, app_name : str) -> pathlib.Path:
    """
    Create the temporary debug config
    """

    # Check n_clients
    if n_clients <= 0 : raise ValueError(f"write_debug_config received an invalid value for n_clients: {n_clients}. n_clients must be a positive integer.")
    
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # APP debug config

    # Get the debug config for the specified app
    debug_config_app = config.get_debug_config_app(app_name)

    # Create folder to store debug config
    debug_dir = pathlib.Path("debug")
    debug_dir.mkdir(parents = True, exist_ok = True)

    # Add paths for the debug node config to the app debug config
    debug_config_app['paths_nodes_config'] = []
    for i in range(n_clients) :
        path_debug_config_node_config = debug_dir / f"node_config_client_{i}.toml"
        debug_config_app['paths_nodes_config'].append(str(path_debug_config_node_config))
    
    # Save debug config in the new folder (APP)
    path_debug_config = debug_dir / f"config_{app_name}.toml"
    with path_debug_config.open("w", encoding = "utf-8") as f : toml.dump(debug_config_app, f)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # DATASET/DATA CONNECTOR debug config (synthetic data)

    # Get path for the template of the synthetic debug data connector config 
    debug_config_data_connector = config.get_debug_config_data_connector('synthetic')

    # import pprint
    # pprint.pprint(debug_config_app)

    required_dataset_type = debug_config_app['required_dataset_type']

    # Save debug config in the new folder (Dataset and data_connector)
    for i in range(n_clients) :
        
        # Change the mean of the generated distribution
        debug_config_data_connector['loc'] = i

        # Change the size of the generated data based on the dataset type (e.g. table generate a 2D matrix)
        debug_config_data_connector['size'] = debug_config_data_connector['data_size_based_on_dataset_type'][required_dataset_type]

        # Save the debug config for the data connector of the current client
        path_debug_config_data_connector = debug_dir / f"synth_1_node_{i}.toml"
        with path_debug_config_data_connector.open("w", encoding = "utf-8") as f : toml.dump(debug_config_data_connector, f)

        # Create the node config for the current client, which specifies the path to the data connector debug config
        node_config_current_client = dict(
            synth_1 = dict(
                dataset_types = required_dataset_type,
                dataset_connector_config_file_path = str(path_debug_config_data_connector)
            ),
            # This was add just to show more than 1 entry in the node config
            syth_2 = dict(
                dataset_types = 'fake_dataset_type',
                dataset_connector_config_file_path = str(debug_dir / f"FAKE_PATH_FOR_CLIENT_{i}.toml")
            )
        )

        # Save the node config for the current client
        path_node_config_current_client = debug_dir / f"node_config_client_{i}.toml"
        with path_node_config_current_client.open("w", encoding = "utf-8") as f : toml.dump(node_config_current_client, f)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    return path_debug_config
