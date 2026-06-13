"""
A Flower `ServerApp` that train (classic) ML algorithms on tabular data (i.e. data that can be represented as an array of features and can be stored in table-like data structure)

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import os
import pickle
import toml

from logging import INFO

from flwr.common import ArrayRecord, ConfigRecord, Context, Message, MessageType, RecordDict
from flwr.common.logger import log
from flwr.server import Grid
from flwr.serverapp import strategy

import support_ml_app

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Flower ServerApp

def main(grid: Grid, context: Context, experiment_config : dict) -> None:
    """
    This `ServerApp` train classic ML models through FedAvg.
    """
    
    # Get the app config from the experiment config
    app_config = experiment_config['app_config']

    fields_to_use_for_train = app_config['path_file_with_fields_to_use_for_the_train']

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
