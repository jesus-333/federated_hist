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
from clinnova_fl import fl_apps

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

    if server_config["app"] == "flower_hist" :
        fl_apps.flower_hist.server.main(grid, context, server_config)
    elif server_config["app"] == "flower_ml" :
        pass
    elif server_config["app"] == "flower_k_means" :
        pass
    else :
        raise ValueError(f"Invalid app specified in the server configuration file: {server_config['app']}. Valid options are: {fl_apps.LIST_OF_APPS}")


