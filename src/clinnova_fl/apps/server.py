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
from clinnova_fl.core.config import config_path
from clinnova_fl.apps import LIST_OF_APPS

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    """
    This `ServerApp` construct a histogram from partial-histograms reported by the `ClientApp`s.
    """
    
    # Read the server configuration file
    path_server_config = Path(context.run_config.get("path_server_config", config_path("server_config_hist.toml")))
    server_config = toml.load(path_server_config)
    
    # Check if the config contains the "app" section, which specifies the app to run. If not, raise an error.
    if "app" not in server_config : raise ValueError(f"Error: The provided configuration file does not contain the 'app' section. Currently, the options in the config file are {list(server_config.keys())}.")

    # Check if there are the configuration for the app specified in the "app" section. If not, raise an error.
    if f"{server_config['app']}_config" not in server_config : raise ValueError(f"Error: The provided configuration file does not contain the '{server_config['app']}_config' section, which is required to run the '{server_config['app']}' app. Currently, the options in the config file are {list(server_config.keys())}.")
    
    # Launch the app specified in the configuration file with the corresponding config.
    if server_config["app"] == "flower_hist" :
        from clinnova_fl.apps.flower_hist import server as flower_hist_server
        flower_hist_server.main(grid, context, server_config['flower_hist_config'])
    elif "flower_ml_config" in server_config :
        from clinnova_fl.apps.flower_ml import server as flower_ml_server
        flower_ml_server.main(grid, context, server_config['flower_ml_config'])
    elif "flower_k_means" in server_config :
        from clinnova_fl.apps.flower_k_means import server as flower_k_means_server
        flower_k_means_server.main(grid, context, server_config['flower_k_means_config'])
    else :
        raise ValueError(f"Error: The 'app' value is not valid. Passed value: {server_config['app']}. Valid options are: {LIST_OF_APPS}")
