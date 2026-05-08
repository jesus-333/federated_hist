"""
Flower histogram server app

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

from __future__ import annotations

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import numpy as np
import os
import pickle
import toml

from collections.abc import Iterable
from logging import INFO
from pathlib import Path

from flwr.common import Context, Message
from flwr.common.logger import log
from flwr.server import Grid, ServerApp

from clinnova_fl.core.config import config_path
from clinnova_fl.apps.support_fl import get_data_from_clients, get_node_ids

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# App implementation

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    # Load server config and check values
    path_server_config = Path(context.run_config.get("path_server_config", config_path("server_config_hist.toml")))
    server_config      = toml.load(path_server_config)
 
    # Federation settings
    # min_nodes specify the minimum number of nodes required to start the histogram computation. If not specified, it is set to n_nodes (the total number of nodes connected to the grid).
    # max_number_of_attempts specify the maximum number of attempts to send the messages and receive the results from the clients. If not specified, it is set to 10. If this number is reached, an exception is raised.
    min_nodes              = server_config['min_nodes'] if 'min_nodes' in server_config else server_config['n_nodes']
    max_number_of_attempts = server_config['max_number_of_attempts'] if 'max_number_of_attempts' in server_config else 10
    
    # Histrogram settings
    # This app will create an histrogram with n_bins, distributed between min and max. 
    # bins_variable specify the name, inside the dataset, of the variable for which the histogram will be created. It is used by the clients to create the local histograms and by the server to create the bins.
    # bins_distribution specify how the bins are distributed between min and max. It can be either 'uniform' or 'logarithmic'. In the first case the bins are uniformly distributed, in the second case they are logarithmically distributed.
    max_val, min_val = None, None
    n_bins = server_config['n_bins'] if 'n_bins' in server_config else 10
    bins_variable = server_config['bins_variable'] if 'bins_variable' in server_config else None
    bins_distribution = server_config['bins_distribution'] if 'bins_distribution' in server_config else 'uniform'

    # Check settings
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

    # Predefined min and max could be used. By default they are None
    # If both are provided the round 0 for min-max computation will be skipped, otherwise the missing value will be computed
    # If only one of the two values is provided, the round 0 will be performed to compute the missing value. This allows to use a predefined min and compute the max from the data, or vice versa.
    predefined_min = server_config.get("predefined_min")
    predefined_max = server_config.get("predefined_max")

    # Path to save results
    path_to_save = Path(server_config.get("path_to_save", "./results/"))

    my_config = dict(
        server_round      = -1,
        bins_variable     = bins_variable,
        bins_distribution = bins_distribution
    )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Min and max computation round (round 0)

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
    """
    Saves the final histogram, the bins used to compute the histogram and other info in a specified folder.
    The info is saved in two formats: as a pickle file and as a toml file.
    The histogram and bins are also saved as numpy arrays.
    """
    
    # TODO Check the reason of the : in the bins_variable
    if ":" in info_to_save["bins_variable"]:
        bins_variable_name = info_to_save["bins_variable"].split(":")[1].strip()
    else:
        bins_variable_name = info_to_save["bins_variable"]
    
    # Create path to save results
    path_to_save = os.path.join(path_to_save, bins_variable_name + '/')

    # Add histogram and other info to the dictionary
    info_to_save = dict(info_to_save)
    info_to_save['histogram'] = final_hist
    info_to_save['mean']      = samples_mean
    info_to_save['std']       = samples_std

    # Create folder if it does not exist
    os.makedirs(path_to_save, exist_ok = True)

    # Save info file as a pickle
    with open(path_to_save + f'results_{label}.pkl', 'wb') as f:
        pickle.dump(info_to_save, f)

    # Save info file as a toml
    with open(path_to_save + f'results_{label}.toml', 'w') as f:
        toml.dump(info_to_save, f)

    # Save bins and histogram as numpy arrays
    np.save(path_to_save / f"bins_{label}.npy", np.array(info_to_save["bins"]))
    np.save(path_to_save / f"hist_{label}.npy", final_hist)
