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

    from clinnova_fl.apps import flower_hist

    flower_hist.cli.main_hist(args, flwr_args)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
