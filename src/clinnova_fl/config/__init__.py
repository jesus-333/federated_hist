"""
CLINNOVA FL package. Config module

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

import pathlib

DEBUG_CONFIG_PATH = {
    "flower_hist": pathlib.Path(__file__).resolve().parent / "debug_config" / "hist.toml",
}

