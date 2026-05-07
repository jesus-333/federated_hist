from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd


def read_txt_list(filepath: str | Path) -> list[str]:
    path = Path(filepath)
    return [line.strip() for line in path.read_text().splitlines() if line.strip()]


def write_txt_list(filepath: str | Path, data: list[str]) -> None:
    path = Path(filepath)
    path.write_text("\n".join(data) + ("\n" if data else ""))


def get_ml_data(path_data: str | Path, fields_to_use_for_the_train: Iterable[str] | None = None) -> tuple[np.ndarray, list[int], np.ndarray]:
    dataset_client = pd.read_csv(path_data)
    if fields_to_use_for_the_train is None:
        fields_to_use_for_the_train = [col for col in dataset_client.columns if col != "Diagnosis"]
    x_data = dataset_client[list(fields_to_use_for_the_train)].to_numpy()
    labels_str = dataset_client["Diagnosis"].to_numpy()
    labels_str_to_int = {"Control": 0, "UC": 1, "CD": 2}
    y_data = [labels_str_to_int[label] for label in labels_str]
    return x_data, y_data, labels_str


def get_hist_data(path_client_data: str | Path, bins_variable: str, class_to_filter: str | None = None) -> tuple[np.ndarray, np.ndarray]:
    dataset_client = pd.read_csv(path_client_data)
    data_hist = dataset_client[bins_variable].to_numpy()
    labels_per_sample = dataset_client["Diagnosis"].to_numpy()

    if class_to_filter is not None:
        idx_to_keep = labels_per_sample == class_to_filter
        data_hist = data_hist[idx_to_keep]
        labels_per_sample = labels_per_sample[idx_to_keep]

    return data_hist, labels_per_sample
