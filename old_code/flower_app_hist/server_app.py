"""
A Flower `ServerApp` that constructs a histogram from clients data.

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
@date: September 2025
"""
import numpy as np
import os
import pickle
import time
import toml

from collections.abc import Iterable
from logging import INFO

from flwr.common import Context, Message, MessageType, RecordDict, ConfigRecord
from flwr.common.logger import log
from flwr.server import Grid, ServerApp

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    path_server_config = context.run_config['path_server_config'] if 'path_server_config' in context.run_config else './server_config.toml'
    server_config = toml.load(path_server_config)

    min_nodes              = server_config['min_nodes'] if 'min_nodes' in server_config else server_config['n_nodes']
    max_number_of_attempts = server_config['max_number_of_attempts'] if 'max_number_of_attempts' in server_config else 10
    max, min = None, None
    n_bins = server_config['n_bins'] if 'n_bins' in server_config else 10
    bins_variable = server_config['bins_variable'] if 'bins_variable' in server_config else None
    bins_distribution = server_config['bins_distribution'] if 'bins_distribution' in server_config else 'uniform'

    predefined_min = server_config['predefined_min'] if 'predefined_min' in server_config else None
    predefined_max = server_config['predefined_max'] if 'predefined_max' in server_config else None
    path_to_save = server_config['path_to_save'] if 'path_to_save' in server_config else './results/'

    my_config = dict(server_round = -1, bins_variable = bins_variable, bins_distribution = bins_distribution)

    if predefined_min is None or predefined_max is None :
        log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        log(INFO, "START ROUND for min and max computation (round 0)")
        my_config['server_round'] = 0
        node_ids_round = get_node_ids(grid, min_nodes)
        results_round_zero = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)
        min, max = compute_min_max_federation(results_round_zero)
        if predefined_min is not None : min = predefined_min
        if predefined_max is not None : max = predefined_max
    else :
        min, max = predefined_min, predefined_max

    log(INFO, f"Computed global min: {min}" if predefined_min is None else f"Using predefined min: {min}")
    log(INFO, f"Computed global max: {max}" if predefined_max is None else f"Using predefined max: {max}")
    log(INFO, "END ROUND for min and max computation (round 0)")

    log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    log(INFO, "START ROUND for histogram computation (round 1)")
    if my_config['bins_distribution'] == 'uniform' :
        bins = np.linspace(min, max, n_bins + 1)
    elif my_config['bins_distribution'] == 'logarithmic' :
        if min == 0 :
            min = 1e-10
            bins = np.geomspace(min, max, n_bins + 1)
        elif min < 0 and max > 0 :
            pass
        else :
            bins = np.geomspace(min, max, n_bins + 1)

    log(INFO, f"Using bins: {bins}")
    my_config['server_round'] = 1
    my_config['bins'] = list(bins)
    results_round_one = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)
    final_hist_per_label, samples_mean_per_label, samples_std_per_label = compute_hist(n_bins, results_round_one)
    log(INFO, f"Final histogram (all samples): {final_hist_per_label['all']}")
    for label in ['all', 'UC', 'CD', 'control'] :
        save_results(label, my_config, final_hist_per_label[label], samples_mean_per_label[label], samples_std_per_label[label], path_to_save)

def get_node_ids(grid: Grid, min_nodes: int) -> list[int]:
    all_node_ids : list[int] = []
    while len(all_node_ids) < min_nodes:
        all_node_ids = list(grid.get_node_ids())
        if len(all_node_ids) >= min_nodes:
            break
        log(INFO, "Waiting for nodes to connect...")
        time.sleep(2)
    return all_node_ids

def send_and_receive_data(grid: Grid, node_ids: list[int], server_round: int, my_config : dict = None) :
    messages = []
    recorddict = RecordDict()
    if my_config is not None : recorddict['my_config'] = ConfigRecord(my_config)
    for node_id in node_ids:
        message = Message(content = recorddict, message_type = MessageType.QUERY, dst_node_id = node_id, group_id = str(server_round))
        messages.append(message)
    replies = grid.send_and_receive(messages)
    log(INFO, "Received %s/%s results", len(replies), len(messages))
    for rep in replies :
        if rep.has_error():
            return None
    return replies

def get_data_from_clients(grid: Grid, node_ids : list[int], my_config : dict = None, max_number_of_attempts : int = 10) -> list[Message]:
    n_attempts = 0
    while (True) :
        results = send_and_receive_data(grid, node_ids, server_round = 0, my_config = my_config)
        if results is not None :
            break
        else :
            n_attempts += 1
            log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
            if n_attempts >= max_number_of_attempts :
                raise Exception(f"Error in receiving data from clients during round {my_config['server_round']}. Maximum number of attempts ({max_number_of_attempts}) reached")
            time.sleep(2)
    return results

def compute_min_max_federation(results_round_zero: Iterable[Message]) -> tuple[float, float]:
    min_list = []
    max_list = []
    for rep in results_round_zero :
        query_results = rep.content["query_results"]
        min_list.append(query_results["min"])
        max_list.append(query_results["max"])
    return min(min_list), max(max_list)

def compute_hist(n_bins : int, results_round_one: Iterable[Message]) -> tuple[dict[str, np.ndarray], dict[str, float], dict[str, float]]:
    labels_list = ['all', 'UC', 'CD', 'control']
    final_hist_per_label = dict()
    samples_mean_per_label = dict()
    samples_std_per_label = dict()
    for label in labels_list :
        final_hist = np.zeros(n_bins, dtype = int)
        mean_list = []
        std_list  = []
        n_samples_list = []
        for rep in results_round_one :
            query_results = rep.content["query_results"]
            local_hist = query_results[f"histogram_{label}"]
            final_hist += np.array(local_hist)
            mean_list.append(query_results[f"average_{label}"])
            std_list.append(query_results[f"std_{label}"])
            n_samples_list.append(np.sum(local_hist))
        samples_mean = np.average(mean_list, weights = n_samples_list)
        samples_std  = np.average(std_list , weights = n_samples_list)
        final_hist_per_label[label]   = final_hist
        samples_mean_per_label[label] = samples_mean
        samples_std_per_label[label]  = samples_std
    return final_hist_per_label, samples_mean_per_label, samples_std_per_label

def save_results(label : str, info_to_save : dict, final_hist : np.ndarray, samples_mean : float, samples_std : float, path_to_save : str) -> None :
    if ":" in info_to_save['bins_variable'] :
        bins_variable_name = info_to_save['bins_variable'].split(":")[1].strip()
    else :
        bins_variable_name = info_to_save['bins_variable']
    path_to_save = os.path.join(path_to_save, bins_variable_name + '/')
    info_to_save['histogram'] = final_hist
    info_to_save['mean']      = samples_mean
    info_to_save['std']       = samples_std
    os.makedirs(path_to_save, exist_ok = True)
    with open(path_to_save + f'results_{label}.pkl', 'wb') as f:
        pickle.dump(info_to_save, f)
    with open(path_to_save + f'results_{label}.toml', 'w') as f:
        toml.dump(info_to_save, f)
    np.save(path_to_save + f'bins_{label}.npy', np.array(info_to_save['bins']))
    np.save(path_to_save + f'hist_{label}.npy', final_hist)
