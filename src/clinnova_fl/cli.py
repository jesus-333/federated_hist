from __future__ import annotations

from argparse import ArgumentParser
import subprocess
from pathlib import Path

from clinnova_fl.core.config import PROJECT_ROOT, config_path


def _build_parser(default_config: Path, description: str) -> ArgumentParser:
    parser = ArgumentParser(description=description)
    parser.add_argument("--config", type=Path, default=default_config, help="Path to the Flower server config file")
    return parser


def launch_ml(argv: list[str] | None = None) -> int:
    parser = _build_parser(config_path("server_config_ml.toml"), "Launch the Flower ML app")
    args = parser.parse_args(argv)
    command = [
        "flwr",
        "run",
        "--stream",
        "--run-config",
        f'path_server_config="{args.config.resolve()}"',
        "./flower_app_ml/",
        "remote-ml_app",
    ]
    return subprocess.call(command, cwd=PROJECT_ROOT)


def launch_hist(argv: list[str] | None = None) -> int:
    parser = _build_parser(config_path("server_config_hist.toml"), "Launch the Flower histogram app")
    args = parser.parse_args(argv)
    command = [
        "flwr",
        "run",
        "--stream",
        "--run-config",
        f'path_server_config="{args.config.resolve()}"',
        "./",
        "remote-hist",
    ]
    return subprocess.call(command, cwd=PROJECT_ROOT)


def main_ml() -> int:
    return launch_ml()


def main_hist() -> int:
    return launch_hist()
