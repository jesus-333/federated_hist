"""
A Flower `ClientApp` that train (classic) ML algorithms on tabular data (i.e. data that can be represented as an array of features and can be stored in table-like data structure)

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>

"""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

# Module Imports
import os
import pickle
import warnings

# Specific imports
from logging import INFO, DEBUG

# Flower imports
from flwr.common import ArrayRecord, Context, Message, MetricRecord, RecordDict
from flwr.common.logger import log

# Internal imports
from clinnova_fl.dataset import tabular
from clinnova_fl.apps.flower_ml_tabular.ml_models import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def train(msg: Message, context: Context, dataset_istance : tabular.dataset):
    """
    Train the model on local data.
    """

    # Get ml model config
    app_config = msg.content["config"]
    ml_model_name = app_config['ml_model_name']

    # Fields (features) to use for the training
    # fields_to_use_for_train = app_config['path_file_with_fields_to_use_for_the_train']
    fields_to_use_for_the_train = app_config['fields_to_use_for_the_train'] if 'fields_to_use_for_the_train in app_config' else None
    n_features = app_config['n_features'] if fields_to_use_for_the_train is None else len(fields_to_use_for_the_train)

    # Create ml model
    ml_model = generic.get_ml_model(app_config['ml_model_name'], app_config['ml_model_config'])

    # Apply received parameters
    params = msg.content["arrays"].to_numpy_ndarrays()
    ml_model.init_params(app_config['num_classes'], n_features) # Required otherwise set_params will fail because the model parameters are not initialized yet
    ml_model.set_params(params) # Set the model parameters to the received parameters.
    
    # Check if the dataset has labels, if not raise an error because we cannot train a model without labels
    if dataset_istance.labels is None : raise ValueError("This dataset currently does not support training because it does not have labels. Please use a dataset with labels to train the model.")

    # Load the data
    x_train, y_train = dataset_istance[:]

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Training/Fitting

    # Train the model on local data
    # Ignore convergence failure due to low local epochs
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ml_model.fit(x_train, y_train)

    # Extract the trained model parameters
    params_trained = ml_model.get_params()
    model_record = ArrayRecord(params_trained)

    log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    log(INFO, "Model trained")
    log(DEBUG, f"Parameters : {params_trained}")
    
    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Metrics computation

    # Check if the model is a regression model or not
    if ml_model_name == 'LASSO' : regression = True
    else : regression = False
    
    # Compute and save the metrics on the local data
    metrics = ml_model.compute_metrics(y_train, ml_model.predict(x_train), regression = regression)
    metrics['num-examples'] = len(x_train)
    metric_record = MetricRecord(metrics)

    log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    log(INFO, "Metrics computed")
    log(INFO, f"{metric_record}")

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Send the results to the server

    # Construct a Message with the results
    content = RecordDict({"arrays": model_record, "metrics": metric_record})

    # Save the model weights locally
    path_to_save_model = context.node_config['path_to_save_model'] if 'path_to_save_model' in context.node_config else './'
    os.makedirs(path_to_save_model, exist_ok = True)
    with open(f'{path_to_save_model}trained_params_{ml_model_name}_node_{dataset_istance.dataset_id}.pkl', "wb") as f : pickle.dump(params, f) # TODO : Use Pathlib instead of os.path

    return Message(content = content, reply_to = msg)

# Keep only as a reminder
# def query(msg : Message, context : Context) :
#     """
#     Send the weights of the trained model to the server.
#
#     Implemented to obtain the model weights of a single nodes outside the FL process. From what I see the FedAvg strategy only return the finale model weights after the last round.
#     For the PoC I also need the model weights of each node to show the difference between the models trained on different datasets.
#     """
#     
#     # Get config
#     node_id = context.node_config['partition-id']
#     path_to_save_model = context.node_config['path_to_save_model'] if 'path_to_save_model' in context.node_config else './'
#     my_config = msg.content['my_config']
#
#     # Load the model weights
#     ml_model_name = my_config['ml_model_name']
#     with open(f"{path_to_save_model}/trained_params_{ml_model_name}_node_{node_id}.pkl", "rb") as f : params = pickle.load(f)
#     
#     model_weights = dict()
#     if my_config['ml_model_name'] == 'SVM' :
#         # For SVM the params are [coef, intercept], coef is of shape (n_classes, n_features)
#         for i in range(len(params[0])) :
#             model_weights[f'coef_class_{i}'] = list(params[0][i])
#
#         model_weights['intercept'] = list(params[1])
#     elif my_config['ml_model_name'] == 'LASSO' :
#         model_weights['coef'] = list(params[0])
#         model_weights['intercept'] = list(params[1])
#
#     # Prepare the Message to send the model weights to the server
#     model_record = MetricRecord(model_weights)
#     reply_content = RecordDict({"query_results": model_record})
#     # reply_content = RecordDict({"query_results": MetricRecord(query_results)})
#
#     return Message(content = reply_content, reply_to = msg)

def evaluate(message: Message, context: Context) -> Message :
    """
    At the moment the evaluate function is not used.
    It is implemented as a placeholder that simply echoes back fixed metrics to avoid errors.
    """

    # Construct and return reply Message
    metrics = {
        "mse": 1.0,
        "mae": 1.0,
        "num-examples": 42,
    }
    metric_record = MetricRecord(metrics)
    content = RecordDict({"metrics": metric_record})

    return Message(content, reply_to = message)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

