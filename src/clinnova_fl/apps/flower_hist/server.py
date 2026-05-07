"""
Flower histogram server app

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

from __future__ import annotations

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import pickle
import time
from collections.abc import Iterable
from logging import INFO
from pathlib import Path

import numpy as np
import toml
from flwr.common import ConfigRecord, Context, Message, MessageType, RecordDict
from flwr.common.logger import log
from flwr.server import Grid, ServerApp

from clinnova_fl.core.config import config_path

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# App implementation

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    path_server_config = Path(context.run_config.get("path_server_config", config_path("server_config_hist.toml")))
    server_config = toml.load(path_server_config)

    min_nodes = server_config.get("min_nodes", server_config["n_nodes"])
    max_number_of_attempts = server_config.get("max_number_of_attempts", 10)
    n_bins = server_config.get("n_bins", 10)
    bins_variable = server_config.get("bins_variable")
    bins_distribution = server_config.get("bins_distribution", "uniform")

    if min_nodes <= 0:
        raise ValueError(f"Invalid value for min_nodes: {min_nodes}. It must be a positive integer")
    if max_number_of_attempts <= 0:
        raise ValueError(f"Invalid value for max_number_of_attempts: {max_number_of_attempts}. It must be a positive integer")
    if n_bins <= 0:
        raise ValueError(f"Invalid value for n_bins: {n_bins}. It must be a positive integer")
    if bins_variable is None:
        raise ValueError("bins_variable must be specified in the server config file")
    if bins_distribution not in ["uniform", "logarithmic"]:
        raise ValueError(f"Invalid value for bins_distribution: {bins_distribution}. It must be either 'uniform' or 'logarithmic'")

    predefined_min = server_config.get("predefined_min")
    predefined_max = server_config.get("predefined_max")
    path_to_save = Path(server_config.get("path_to_save", "./results/"))

    my_config = dict(server_config=server_config)
    my_config = dict(server_round=-1, bins_variable=bins_variable, bins_distribution=bins_distribution)

    if predefined_min is None or predefined_max is None:
        log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        log(INFO, "START ROUND for min and max computation (round 0)")
        my_config["server_round"] = 0
        node_ids_round = get_node_ids(grid, min_nodes)
        results_round_zero = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)
        min_val, max_val = compute_min_max_federation(results_round_zero)
        if predefined_min is not None:
            min_val = predefined_min
        if predefined_max is not None:
            max_val = predefined_max
    else:
        min_val, max_val = predefined_min, predefined_max

    log(INFO, f"Computed global min: {min_val}" if predefined_min is None else f"Using predefined min: {min_val}")
    log(INFO, f"Computed global max: {max_val}" if predefined_max is None else f"Using predefined max: {max_val}")
    log(INFO, "END ROUND for min and max computation (round 0)")

    log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    log(INFO, "START ROUND for histogram computation (round 1)")
    if my_config["bins_distribution"] == "uniform":
        bins = np.linspace(min_val, max_val, n_bins + 1)
    else:
        if min_val == 0:
            min_val = 1e-10
        bins = np.geomspace(min_val, max_val, n_bins + 1)
    log(INFO, f"Using bins: {bins}")

    my_config["server_round"] = 1
    my_config["bins"] = list(bins)
    results_round_one = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)
    final_hist_per_label, samples_mean_per_label, samples_std_per_label = compute_hist(n_bins, results_round_one)
    log(INFO, f"Final histogram (all samples): {final_hist_per_label['all']}")
    for label in ["all", "UC", "CD", "control"]:
        save_results(label, my_config, final_hist_per_label[label], samples_mean_per_label[label], samples_std_per_label[label], path_to_save)


def get_node_ids(grid: Grid, min_nodes: int) -> list[int]:
    all_node_ids: list[int] = []
    while len(all_node_ids) < min_nodes:
        all_node_ids = list(grid.get_node_ids())
        if len(all_node_ids) >= min_nodes:
            break
        log(INFO, "Waiting for nodes to connect...")
        time.sleep(2)
    return all_node_ids


def send_and_receive_data(grid: Grid, node_ids: list[int], server_round: int, my_config: dict | None = None):
    messages = []
    recorddict = RecordDict()
    if my_config is not None:
        recorddict["my_config"] = ConfigRecord(my_config)
    for node_id in node_ids:
        messages.append(Message(content=recorddict, message_type=MessageType.QUERY, dst_node_id=node_id, group_id=str(server_round)))
    replies = grid.send_and_receive(messages)
    log(INFO, "Received %s/%s results", len(replies), len(messages))
    for rep in replies:
        if rep.has_error():
            return None
    return replies


def get_data_from_clients(grid: Grid, node_ids: list[int], my_config: dict | None = None, max_number_of_attempts: int = 10) -> list[Message]:
    n_attempts = 0
    while True:
        results = send_and_receive_data(grid, node_ids, server_round=0, my_config=my_config)
        if results is not None:
            break
        n_attempts += 1
        log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
        if n_attempts >= max_number_of_attempts:
            raise Exception(f"Error in receiving data from clients during round {my_config['server_round']}. Maximum number of attempts ({max_number_of_attempts}) reached")
        time.sleep(2)
    return results


def compute_min_max_federation(results_round_zero: Iterable[Message]) -> tuple[float, float]:
    min_list = []
    max_list = []
    for rep in results_round_zero:
        query_results = rep.content["query_results"]
        min_list.append(query_results["min"])
        max_list.append(query_results["max"])
    return min(min_list), max(max_list)


def compute_hist(n_bins: int, results_round_one: Iterable[Message]) -> tuple[dict[str, np.ndarray], dict[str, float], dict[str, float]]:
    labels_list = ["all", "UC", "CD", "control"]
    final_hist_per_label = {}
    samples_mean_per_label = {}
    samples_std_per_label = {}
    for label in labels_list:
        final_hist = np.zeros(n_bins, dtype=int)
        mean_list = []
        std_list = []
        n_samples_list = []
        for rep in results_round_one:
            query_results = rep.content["query_results"]
            local_hist = query_results[f"histogram_{label}"]
            final_hist += np.array(local_hist)
            mean_list.append(query_results[f"average_{label}"])
            std_list.append(query_results[f"std_{label}"])
            n_samples_list.append(np.sum(local_hist))
        samples_mean = np.average(mean_list, weights=n_samples_list)
        samples_std = np.average(std_list, weights=n_samples_list)
        final_hist_per_label[label] = final_hist
        samples_mean_per_label[label] = samples_mean
        samples_std_per_label[label] = samples_std
    return final_hist_per_label, samples_mean_per_label, samples_std_per_label


def save_results(label: str, info_to_save: dict, final_hist: np.ndarray, samples_mean: float, samples_std: float, path_to_save: str | Path) -> None:
    if ":" in info_to_save["bins_variable"]:
        bins_variable_name = info_to_save["bins_variable"].split(":")[1].strip()
    else:
        bins_variable_name = info_to_save["bins_variable"]
    path_to_save = Path(path_to_save) / bins_variable_name
    info_to_save = dict(info_to_save)
    info_to_save["histogram"] = final_hist
    info_to_save["mean"] = samples_mean
    info_to_save["std"] = samples_std
    path_to_save.mkdir(parents=True, exist_ok=True)
    with open(path_to_save / f"results_{label}.pkl", "wb") as f:
        pickle.dump(info_to_save, f)
    with open(path_to_save / f"results_{label}.toml", "w") as f:
        toml.dump(info_to_save, f)
    np.save(path_to_save / f"bins_{label}.npy", np.array(info_to_save["bins"]))
    np.save(path_to_save / f"hist_{label}.npy", final_hist)
