from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
PACKAGE_ROOT = SRC_ROOT / "clinnova_fl"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
STREAMLIT_DIR = PROJECT_ROOT / "streamlit_interface"
OTHER_SCRIPTS_DIR = PROJECT_ROOT / "other_scripts"
RESULTS_DIR = PROJECT_ROOT / "results"


def project_path(*parts: str) -> Path:
    return PROJECT_ROOT.joinpath(*parts)


def config_path(name: str) -> Path:
    return CONFIG_DIR / name


def data_path(name: str) -> Path:
    return DATA_DIR / name


def streamlit_path(name: str) -> Path:
    return STREAMLIT_DIR / name


def other_script_path(name: str) -> Path:
    return OTHER_SCRIPTS_DIR / name
