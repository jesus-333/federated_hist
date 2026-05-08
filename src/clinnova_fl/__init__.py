"""
CLINNOVA FL package.

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

from pathlib import Path

DEBUG_CONFIG_PATH = {
    "flower_hist": Path(__file__).resolve().parent / "generic" / "debug_config" / "hist.toml",
}
