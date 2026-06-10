"""
CLINNOVA FL package. Config module

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import pathlib

DEBUG_CONFIG_PATH = dict(
    # Applications
    flower_hist = pathlib.Path(__file__).resolve().parent / "debug_config" / "hist.toml",
    flower_ml   = pathlib.Path(__file__).resolve().parent / "debug_config" / "ml.toml", # TO DO: create the debug config for the flower_ml app

    # Data connectors 
    synthetic = pathlib.Path(__file__).resolve().parent / "debug_config" / "synthetic_data_connector.toml",
)


