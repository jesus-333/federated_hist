"""
A Flower `ServerApp` that train a machine learning algorithm.
Currently implemented algorithm SVM, LASSO

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

from logging import INFO

from flwr.common import ArrayRecord, ConfigRecord, Context, Message, MessageType, RecordDict
from flwr.common.logger import log
from flwr.server import Grid, ServerApp
from flwr.serverapp import strategy

import support_ml_app

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    import pathlib
    print(pathlib.Path().resolve())
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

    path_server_config = context.run_config['path_server_config']
    server_config = toml.load(path_server_config)

    fields_to_use_for_train = support_ml_app.read_txt_list(server_config['path_file_with_fields_to_use_for_the_train'])
    x_server, y_server, _ = support_ml_app.get_data(server_config['path_server_data'], fields_to_use_for_train)
    path_to_save = server_config['path_to_save'] if 'path_to_save' in server_config else './results/'

    my_config = server_config['ml_algorithm_config']
    my_config['ml_model_name'] = server_config['ml_model_name']
    my_config['fields_to_use_for_the_train'] = fields_to_use_for_train

    ml_model = support_ml_app.get_ml_model(my_config['ml_model_name'], my_config)
    log(INFO, f"ML Model created: {ml_model}")

    support_ml_app.set_initial_params(my_config['ml_model_name'], ml_model, 3, x_server.shape[1])
    arrays = ArrayRecord(support_ml_app.get_model_params(my_config['ml_model_name'], ml_model))
    fl_strategy = strategy.FedAvg()
    train_config = ConfigRecord(config_dict = {'config': my_config})

    result = fl_strategy.start(
        grid = grid,
        initial_arrays = arrays,
        num_rounds = server_config['num_rounds'],
        train_config = train_config
    )

    params_final = result.arrays.to_numpy_ndarrays()
    support_ml_app.set_model_params(my_config['ml_model_name'], ml_model, params_final)

    os.makedirs(path_to_save, exist_ok = True)
    with open(f'{path_to_save}/final_params_{my_config["ml_model_name"]}.pkl', "wb") as f : pickle.dump(params_final, f)

    n_nodes = server_config['n_nodes']
    node_ids = get_node_ids(grid, n_nodes)
    list_params_per_node = get_model_weights_from_clients(grid, node_ids, my_config)
    for i in range(n_nodes) :
        with open(f'{path_to_save}/trained_params_{my_config["ml_model_name"]}_node_{node_ids[i]}.pkl', "wb") as f :
            pickle.dump(list_params_per_node[i], f)

def get_node_ids(grid: Grid, min_nodes: int) -> list[int]:
    all_node_ids : list[int] = []
    while len(all_node_ids) < min_nodes:
        all_node_ids = list(grid.get_node_ids())
        if len(all_node_ids) >= min_nodes:
            break
        log(INFO, "Waiting for nodes to connect...")
        time.sleep(2)
    return all_node_ids

def send_and_receive_data(grid: Grid, node_ids: list[int], server_round: int, my_config : dict = None):
    messages = []
    record_dict = RecordDict()
    if my_config is not None : record_dict['my_config'] = ConfigRecord(my_config)
    for node_id in node_ids:
        message = Message(content = record_dict, message_type = MessageType.QUERY, dst_node_id = node_id, group_id = str(server_round))
        messages.append(message)
    replies = grid.send_and_receive(messages)
    log(INFO, "Received %s/%s results", len(replies), len(messages))
    for rep in replies :
        if rep.has_error():
            return None
    return replies

def get_model_weights_from_clients(grid: Grid, node_ids : list[int], my_config : dict = None, max_number_of_attempts : int = 10) -> list:
    n_attempts = 0
    while (True) :
        results = send_and_receive_data(grid, node_ids, server_round = 0, my_config = my_config)
        if results is not None :
            break
        else :
            n_attempts += 1
            log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
            if n_attempts >= max_number_of_attempts :
                raise Exception(f"Error in receiving data from clients. Maximum number of attempts ({max_number_of_attempts}) reached")
            time.sleep(2)

    list_params_per_node = []
    for rep in results :
        query_results = rep.content["query_results"]
        tmp_params = []
        if my_config['ml_model_name'] == 'SVM' :
            tmp_coef = []
            for i in range(3) :
                tmp_coef.append(np.array(query_results[f'coef_class_{i}']))
            tmp_params.append(np.array(tmp_coef))
            tmp_params.append(query_results['intercept'])
        elif my_config['ml_model_name'] == 'LASSO' :
            tmp_params.append(query_results['coef'])
            tmp_params.append(query_results['intercept'])
        list_params_per_node.append(tmp_params)

    return list_params_per_node
