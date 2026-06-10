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

def get_debug_config_app(app_name : str) -> dict :
    
    # Note that DEBUG_CONFIG_PATH is a dictionary defined in the __init__.py file of this config module, which maps app names to the paths of their respective debug configuration files.
    print(DEBUG_CONFIG_PATH)

    template_path = DEBUG_CONFIG_PATH[app_name]

    debug_config_app = toml.load(template_path)

    return debug_config_app

def get_debug_config_data_connector(data_type : str) -> dict :
    print(DEBUG_CONFIG_PATH)

    template_path = DEBUG_CONFIG_PATH[data_type]

    debug_config_data_connector = toml.load(template_path)

    return debug_config_data_connector

    # I know. This function is identical to the previous one. 
    # But I prefer to have it separated for now, in case I want to add some data-connector-specific processing in the future.
