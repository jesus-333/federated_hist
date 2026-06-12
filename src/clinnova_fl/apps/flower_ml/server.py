"""
A Flower `ServerApp` that train a machine learning algorithm

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Flower ServerApp

def main(grid: Grid, context: Context, experiment_config : dict) -> None:
    """
    This `ServerApp` train a ML model through FedAvg.
    """

    app_config = experiment_config['app_config']

    path_server_config = context.run_config['path_server_config']
    server_config = toml.load(path_server_config)

    fields_to_use_for_train = support_ml_app.read_txt_list(server_config['path_file_with_fields_to_use_for_the_train'])

    # Load server data
    x_server, y_server, _ = support_ml_app.get_data(server_config['path_server_data'], fields_to_use_for_train)
    
    # Path to save the final results
    path_to_save = server_config['path_to_save'] if 'path_to_save' in server_config else './results/'

    # Dictionary used to communicate with the clients
    my_config = server_config['ml_algorithm_config']
    my_config['ml_model_name'] = server_config['ml_model_name']
    my_config['fields_to_use_for_the_train'] = fields_to_use_for_train

    # Create ml model
    ml_model = support_ml_app.get_ml_model(my_config['ml_model_name'], my_config)
    log(INFO, f"ML Model created: {ml_model}")

    # Setting initial parameters (it is required by flower) and convert them in an ArrayRecord representation
    support_ml_app.set_initial_params(my_config['ml_model_name'], ml_model, 3, x_server.shape[1])
    arrays = ArrayRecord(support_ml_app.get_model_params(my_config['ml_model_name'], ml_model))
    
    # Create FL strategy
    fl_strategy = strategy.FedAvg()

    # Create train config
    train_config = ConfigRecord(config_dict = my_config)
    
    # Federated training
    result = fl_strategy.start(
        grid = grid,
        initial_arrays = arrays,
        num_rounds = server_config['num_rounds'],
        train_config = train_config
    )
    
    # Get the results
    # Note that the function to_numpy_ndarrays() return the ArrayRecord as a list of NumPy ndarray.
    params_final = result.arrays.to_numpy_ndarrays()
    support_ml_app.set_model_params(my_config['ml_model_name'], ml_model, params_final)

    # Save the final weights of the model
    os.makedirs(path_to_save, exist_ok = True)
    with open(f'{path_to_save}/final_params_{my_config["ml_model_name"]}.pkl', "wb") as f : pickle.dump(params_final, f)

    # Get the model weights of the single node
    n_nodes = server_config['n_nodes']
    node_ids = get_node_ids(grid, n_nodes)
    list_params_per_node = get_model_weights_from_clients(grid, node_ids, my_config)
    
    # Save the model weights of the single nodes
    for i in range(n_nodes) :
        with open(f'{path_to_save}/trained_params_{my_config["ml_model_name"]}_node_{node_ids[i]}.pkl', "wb") as f :
            pickle.dump(list_params_per_node[i], f)
