"""
A Flower `ServerApp` that train (classic) ML algorithms on tabular data (i.e. data that can be represented as an array of features and can be stored in table-like data structure)

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

# Module imports
import os
import pickle

# Specific imports
from logging import INFO

# Flower imports
from flwr.common import ArrayRecord, ConfigRecord, Context
from flwr.common.logger import log
from flwr.server import Grid
from flwr.serverapp import strategy

# Internal imports
from clinnova_fl.apps.flower_ml_tabular.ml_models import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Flower ServerApp

def main(grid: Grid, context: Context, experiment_config : dict) -> None:
    """
    This `ServerApp` train classic ML models through FedAvg.
    """
    
    # Get the app config from the experiment config
    # TODO : Add check to the config for specific algorithm. E.g. LDA should need only 1 federated round
    app_config = experiment_config['app_config']
    
    # Fields (features) to use for the training
    # fields_to_use_for_train = app_config['path_file_with_fields_to_use_for_the_train']
    fields_to_use_for_the_train = app_config['fields_to_use_for_the_train'] if 'fields_to_use_for_the_train in app_config' else None
    n_features = app_config['n_features'] if fields_to_use_for_the_train is None else len(fields_to_use_for_the_train)

    # Path to save the final histogram
    path_to_save = app_config['path_to_save'] if 'path_to_save' in app_config else './results/'

    # Dictionary used to communicate with the clients
    # my_config = app_config['ml_model_config']
    # my_config['ml_model_name'] = app_config['ml_model_name']
    # my_config['fields_to_use_for_the_train'] = fields_to_use_for_the_train

    # Create ml model
    ml_model = generic.get_ml_model(app_config['ml_model_name'], app_config['ml_model_config'])
    log(INFO, f"ML Model created: {ml_model}")

    # Setting initial parameters (it is required by flower) and convert them in an ArrayRecord representation
    # support_ml_app.set_initial_params(my_config['ml_model_name'], ml_model, app_config['num_classes'], n_features)
    ml_model.init_params(app_config['num_classes'], n_features)
    arrays = ArrayRecord(ml_model.get_params())

    # Create FL strategy
    fl_strategy = strategy.FedAvg()

    # Create train config
    train_config = ConfigRecord(config_dict = app_config)
    
    # Federated training
    result = fl_strategy.start(
        grid = grid,
        initial_arrays = arrays,
        num_rounds = app_config['num_rounds'],
        train_config = train_config
    )
    
    # Get the results
    # Note that the function to_numpy_ndarrays() return the ArrayRecord as a list of NumPy ndarray.
    params_final = result.arrays.to_numpy_ndarrays()
    # support_ml_app.set_model_params(my_config['ml_model_name'], ml_model, params_final)

    # Save the final weights of the model
    os.makedirs(path_to_save, exist_ok = True)
    with open(f'{path_to_save}/final_params_{my_config["ml_model_name"]}.pkl', "wb") as f : pickle.dump(params_final, f)
