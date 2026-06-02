"""
Decide if keeping this file or not.
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from __future__ import annotations

import pathlib
import toml

from clinnova_fl.config import DEBUG_CONFIG_PATH

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

PROJECT_ROOT      = pathlib.Path(__file__).resolve().parents[3]
SRC_ROOT          = PROJECT_ROOT / "src"
PACKAGE_ROOT      = SRC_ROOT     / "clinnova_fl"
CONFIG_DIR        = PROJECT_ROOT / "config"
DATA_DIR          = PROJECT_ROOT / "data"
STREAMLIT_DIR     = PROJECT_ROOT / "streamlit_interface"
OTHER_SCRIPTS_DIR = PROJECT_ROOT / "other_scripts"
RESULTS_DIR       = PROJECT_ROOT / "results"

def project_path(*parts : str) -> pathlib.Path:
    return PROJECT_ROOT.joinpath(*parts)

def config_path(name : str) -> pathlib.Path:
    return CONFIG_DIR / name

def data_path(name : str) -> pathlib.Path:
    return DATA_DIR / name

def streamlit_path(name : str) -> pathlib.Path:
    return STREAMLIT_DIR / name

def other_script_path(name : str) -> pathlib.Path:
    return OTHER_SCRIPTS_DIR / name

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_debug_config(app_name : str) -> dict :

    print(DEBUG_CONFIG_PATH)
    template_path = DEBUG_CONFIG_PATH[app_name]

    debug_config = toml.load(template_path)

    return debug_config
