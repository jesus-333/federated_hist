"""
A generic wrapper for the ServerApp class, which is used to call the specific server-side application based on the configuration file received as input.
Based on the configuration file received as input a different server-side application will be used.

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

# Full package imports
import numpy as np
import os
import pickle
import toml

# Specific imports
from collections.abc import Iterable
from logging import INFO
from pathlib import Path

# Flower imports
from flwr.common import Context, Message, MessageType, RecordDict, ConfigRecord
from flwr.common.logger import log
from flwr.server import Grid, ServerApp

# Internal imports
# from clinnova_fl.generic.config import config_path
from clinnova_fl.apps import LIST_OF_APPS

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    """
    """

    # Check if app is specified in the configuration. If not, raise an error.
    if "app" not in context.run_config : raise ValueError(f"Error: The provided configuration file does not contain the 'app' key, which is required to run the an app. Currently, the options in the config file are {list(context.run_config.keys())}.")
    
    # Check that the specified app is valid. If not, raise an error.
    if context.run_config["app"] not in LIST_OF_APPS : raise ValueError(f"Error: The 'app' value is not valid. Passed value: {context.run_config['app']}. Valid options are: {LIST_OF_APPS}")

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # Check if the app configuration file path is specified in the configuration. If not, raise an error.
    if "path_app_config" not in context.run_config : raise ValueError(f"Error: The provided configuration file does not contain the 'path_app_config' key, which is required to run the an app. Currently, the options in the config file are {list(context.run_config.keys())}.")

    # Load app config
    app_config = read_toml_config(Path(context.run_config["path_app_config"]))

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Check if dataset_id is specified in the app configuration. If not, raise an error.
    if "dataset_id" not in app_config : raise ValueError(f"Error: The provided app configuration file does not contain the 'dataset_id' key, which is required to run the an app. Currently, the options in the app config file are {list(app_config.keys())}.")

    # Load data connector config
    dataset_id = read_toml_config(Path(app_config['dataset_id ']))

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Prepare experiment config

    experiment_config = dict(
        app = context.run_config["app"],
        app_config = app_config,
        dataset_id = dataset_id,
        simulation = context.run_config['simulation']
    )

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    # Import the requested app
    if context.run_config["app"] == "flower_hist" :
        from clinnova_fl.apps.flower_hist import server
    elif context.run_config["app"] == "flower_ml" :
        from clinnova_fl.apps.flower_ml import server
    elif context.run_config["app"] == "flower_k_means" :
        from clinnova_fl.apps.flower_k_means import server
    
    # Launch the app
    server.main(grid, context, experiment_config)

def read_toml_config(path_toml_config : Path) -> dict :
    """
    Read a toml configuration file and return it as a dictionary.
    """
    try :
        config = toml.load(path_toml_config)
        return config
    except Exception as e :
        raise ValueError(f"Error while reading the configuration file at {path_toml_config}.\n\nError raised :\n{e}")
