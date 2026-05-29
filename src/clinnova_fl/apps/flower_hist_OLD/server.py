"""
A Flower `ServerApp` that constructs a histogram from clients data.

The computation is performed in two rounds :
- Round 0 : the server sends a message to the clients, asking them to compute the local min and max of the variable of interest. The server then computes the global min and max, which will be used to create the bins for the histogram (Note that this round can be skipped if the min and max are predefined in the server config file).
- Round 1 : the server sends a message to the clients, asking them to compute the local histogram of the variable of interest, using the bins computed in round 0. The server then sums the local histograms to obtain the final histogram.

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

# Full package imports
import numpy as np
import os
import pickle
import toml

# Specific imports
from collections.abc import Iterable
from logging import INFO
from pathlib import Path

# Flower imports
from flwr.common import Context, Message, MessageType, RecordDict, ConfigRecord
from flwr.common.logger import log
from flwr.server import Grid

# Internal imports
from clinnova_fl.apps.support_fl import get_data_from_clients, get_node_ids
from clinnova_fl.apps.flower_hist import support

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Flower ServerApp

def main(grid: Grid, context: Context, server_config : dict) -> None:
    """
    This `ServerApp` construct a histogram from partial-histograms reported by the `ClientApp`s.
    """

    # path_server_config = context.run_config['path_server_config'] if 'path_server_config' in context.run_config else './server_config.toml'
    # path_server_config = Path(context.run_config.get("path_server_config", config_path("server_config_hist.toml")))
    # server_config = toml.load(path_server_config)

    # Federation settings
    # min_nodes specify the minimum number of nodes required to start the histogram computation. If not specified, it is set to n_nodes (the total number of nodes connected to the grid).
    # max_number_of_attempts specify the maximum number of attempts to send the messages and receive the results from the clients. If not specified, it is set to 10. If this number is reached, an exception is raised.
    min_nodes              = server_config['min_nodes'] if 'min_nodes' in server_config else server_config['n_nodes']
    max_number_of_attempts = server_config['max_number_of_attempts'] if 'max_number_of_attempts' in server_config else 10
    
    # Histrogram settings
    # This app will create an histrogram with n_bins, distributed between min and max. 
    # bins_variable specify the name, inside the dataset, of the variable for which the histogram will be created. It is used by the clients to create the local histograms and by the server to create the bins.
    # bins_distribution specify how the bins are distributed between min and max. It can be either 'uniform' or 'logarithmic'. In the first case the bins are uniformly distributed, in the second case they are logarithmically distributed.
    max, min = None, None
    n_bins = server_config['n_bins'] if 'n_bins' in server_config else 10
    bins_variable = server_config['bins_variable'] if 'bins_variable' in server_config else None
    bins_distribution = server_config['bins_distribution'] if 'bins_distribution' in server_config else 'uniform'

    # Check settings
    if min_nodes <= 0 :
        raise ValueError(f"Invalid value for min_nodes: {min_nodes}. It must be a positive integer")
    if max_number_of_attempts <= 0 :
        raise ValueError(f"Invalid value for max_number_of_attempts: {max_number_of_attempts}. It must be a positive integer")
    if n_bins <= 0 :
        raise ValueError(f"Invalid value for n_bins: {n_bins}. It must be a positive integer")
    if bins_variable is None :
        raise ValueError("bins_variable must be specified in the server config file")
    if bins_distribution not in ['uniform', 'logarithmic'] :
        raise ValueError(f"Invalid value for bins_distribution: {bins_distribution}. It must be either 'uniform' or 'logarithmic'")
    
    # Predefined min and max could be used. By default they are None
    # If both are provided the round 0 for min-max computation will be skipped, otherwise the missing value will be computed
    # If only one of the two values is provided, the round 0 will be performed to compute the missing value. This allows to use a predefined min and compute the max from the data, or vice versa.
    predefined_min = server_config['predefined_min'] if 'predefined_min' in server_config else None
    predefined_max = server_config['predefined_max'] if 'predefined_max' in server_config else None
    
    # Path to save the final histogram
    path_to_save = server_config['path_to_save'] if 'path_to_save' in server_config else './results/'
    
    # Dictionary used to communicate with the clients
    # my_config = dict(
    #     server_round = -1,
    #     bins_variable = bins_variable,
    #     bins_distribution = bins_distribution
    # )
    my_config = server_config.copy()
    my_config['server_round'] = -1

    # Note that I can use the run_config theoretically but it is read-only. And In this case I need to update the config for each round.
    # So I prefer to use a separate dictionary that I can update as I want and that I can pass as an argument of the get_data_from_clients function, which is the function that send the messages to the clients and receive the results.

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Min and max computation round (round 0)

    if predefined_min is None or predefined_max is None :
        log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        log(INFO, "START ROUND for min and max computation (round 0)")

        # Update config for round 0
        my_config['server_round'] = 0
        
        # Get all node ids
        # Note that this id will be used both for round 0 and round 1
        node_ids_round = get_node_ids(grid, min_nodes)
        
        # Get the min and max from the clients
        results_round_zero = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)

        # Compute global min and max
        min, max = compute_min_max_federation(results_round_zero)
        
        # Overwrite min or max if predefined values are provided
        # Note that only one of this two if could be executed.
        if predefined_min is not None : min = predefined_min
        if predefined_max is not None : max = predefined_max

    else :
        # If both predefined_min and predefined_max are provided, skip the round 0 and use the predefined values
        min, max = predefined_min, predefined_max

    log(INFO, f"Computed global min: {min}" if predefined_min is None else f"Using predefined min: {min}")
    log(INFO, f"Computed global max: {max}" if predefined_max is None else f"Using predefined max: {max}")
    log(INFO, "END ROUND for min and max computation (round 0)")

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # Histogram computation rounds (round 1)

    log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    log(INFO, "START ROUND for histogram computation (round 1)")
    
    # Compute bins
    if my_config['bins_distribution'] == 'uniform' :
        bins = np.linspace(min, max, n_bins + 1)
    elif my_config['bins_distribution'] == 'logarithmic' :
        if min == 0 :
            # Avoid issues with log scale if min is 0
            min = 1e-10
            bins = np.geomspace(min, max, n_bins + 1)
        elif min < 0 and max > 0 :
            # Avoid issues with log scale if min is negative and max is positive
            # TODO Eventually implement a solution for this case
            # Not necessary for the PoC since the min value in the dataset is 0
            pass
        else :
            bins = np.geomspace(min, max, n_bins + 1)

    log(INFO, f"Using bins: {bins}")

    # Update config for round 1
    my_config['server_round'] = 1
    my_config['bins'] = list(bins)
    
    # Get the partial histograms from the clients
    results_round_one = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)
    
    # Compute final histogram
    final_hist_per_label, samples_mean_per_label, samples_std_per_label = compute_hist(n_bins, results_round_one)
    log(INFO, f"Final histogram (all samples): {final_hist_per_label['all']}")

    # Save results
    for label in ['all', 'UC', 'CD', 'control'] :
        save_results(label, my_config, final_hist_per_label[label], samples_mean_per_label[label], samples_std_per_label[label], path_to_save)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Functions for Min-max computation round (Round 0)

def compute_min_max_federation(results_round_zero: Iterable[Message]) -> tuple[float, float]:
    """
    Compute the global min and max from a list of local mins and maxs.

    Parameters
    ----------
    results_round_zero : Iterable[Message]
        List of messages obtained form the clients.
        See https://flower.ai/docs/framework/ref-api/flwr.common.Message.html for more details about the Message class.

    Returns
    -------
    min : float
        The global min.
    max : float
        The global max.
    """
    
    # Lists for storing all local mins and maxs
    min_list = []
    max_list = []

    for rep in results_round_zero :
        # Get the content of the message
        # Note that the key "query_results" is not a predefined key from the Flower framework. It is just a key used in the client app.
        # If you want you could use whatever key you want, as long as it is the same in the client and server app.
        query_results = rep.content["query_results"]

        # The query_results is an istance of the MetricRecord class.
        # See https://flower.ai/docs/framework/ref-api/flwr.common.MetricRecord.html for more details about the MetricRecord class.
        
        # Append local min and max to the lists
        min_list.append(query_results["min"])
        max_list.append(query_results["max"])

    return min(min_list), max(max_list)

def compute_hist(n_bins : int, results_round_one: Iterable[Message]) -> tuple[dict[str, np.ndarray], dict[str, float], dict[str, float]]:
    """
    Compute the final histogram from a list of client histograms.
    It also compute the mean and std of the data, since the clients also send these values.

    Parameters
    ----------
    n_bins : int
        Number of bins in the histogram.
    results_round_one : Iterable[Message]
        List of messages obtained form the clients. They must contain the local histograms.
        See https://flower.ai/docs/framework/ref-api/flwr.common.Message.html for more details about the Message class.

    Returns
    -------
    final_hist_per_label : dict[str, np.ndarray]
        Dictionary containing the final histogram for each label.
        The keys are 'all', 'UC', 'CD', 'control'.
    samples_mean_per_label : dict[str, float]
        Dictionary containing the mean of the data for each label.
        The keys are 'all', 'UC', 'CD', 'control'.
    samples_std_per_label : dict[str, float]
        Dictionary containing the std of the data for each label.
        The keys are 'all', 'UC', 'CD', 'control'.
    """
    
    # Labels
    labels_list = ['all', 'UC', 'CD', 'control']
    
    # Variable to save the results
    final_hist_per_label = dict()
    samples_mean_per_label = dict()
    samples_std_per_label = dict()

    for label in labels_list :
        # Initialize final histogram
        final_hist = np.zeros(n_bins, dtype = int)
        
        # Lists for storing all local means and stds
        mean_list = []
        std_list  = []

        # Used to compute the weighted average of the mean and std
        n_samples_list = []

        for rep in results_round_one :
            # Get query results
            query_results = rep.content["query_results"]

            # Get local histogram
            local_hist = query_results[f"histogram_{label}"]

            # Sum histograms
            final_hist += np.array(local_hist)

            # Append local mean and std to the lists
            mean_list.append(query_results[f"average_{label}"])
            std_list.append(query_results[f"std_{label}"])

            # Append number of samples to the list
            n_samples_list.append(np.sum(local_hist))

        # Compute mean and std of the data
        # TODO Eventually implement the computation of the std as the pooled std (https://en.wikipedia.org/wiki/Pooled_variance)
        samples_mean = np.average(mean_list, weights = n_samples_list)
        samples_std  = np.average(std_list , weights = n_samples_list)

        # Save results
        final_hist_per_label[label]   = final_hist
        samples_mean_per_label[label] = samples_mean
        samples_std_per_label[label]  = samples_std

    return final_hist_per_label, samples_mean_per_label, samples_std_per_label

def save_results(label : str, info_to_save : dict, final_hist : np.ndarray, samples_mean : float, samples_std : float, path_to_save : str) -> None :
    """
    Saves the final histogram, the bins used to compute the histogram and other info in a specified folder.
    The info is saved in two formats: as a pickle file and as a toml file.
    The histogram and bins are also saved as numpy arrays.
    """

    if ":" in info_to_save['bins_variable'] :
        bins_variable_name = info_to_save['bins_variable'].split(":")[1].strip()
    else :
        bins_variable_name = info_to_save['bins_variable']

    path_to_save = os.path.join(path_to_save, bins_variable_name + '/')

    # Add histogram and other info to the dictionary
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

    # Save histogram and bins as numpy arrays
    np.save(path_to_save + f'bins_{label}.npy', np.array(info_to_save['bins']))
    np.save(path_to_save + f'hist_{label}.npy', final_hist)
