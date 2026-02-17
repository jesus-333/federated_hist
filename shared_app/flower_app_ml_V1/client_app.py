"""
A Flower `ClientApp` that train a machine learning algorithm
Currently implemented algorithm are SVM

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
@date: September 2025
"""
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import numpy as np
import os
import pickle
import warnings

from flwr.client import ClientApp
from flwr.common import ArrayRecord, Context, Message, MetricRecord, RecordDict

import support_ml_app

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# warnings.filterwarnings("ignore", category = UserWarning)

# Flower ClientApp
app = ClientApp()

@app.train()
def train(msg: Message, context: Context):
    """
    Train the model on local data.
    """
    
    # Max number of samples to use for generating synthetic data.
    max_n_samples = 1000

    # Get node config
    node_id = context.node_config['partition-id']

    # Get ml model config
    ml_model_config = msg.content["config"]
    ml_model_name = ml_model_config['ml_model_name']

    # Create synthetic data for the train
    n_samples = np.random.randint(100, max_n_samples)
    x_train = np.random.rand(n_samples, ml_model_config['n_features'])
    y_train = np.random.randint(0, ml_model_config['n_classes'], n_samples)

    # Create ml model
    ml_model = support_ml_app.get_ml_model(ml_model_name, ml_model_config)

    # Setting initial parameters
    # Required because the model parameters are not initialized until the fit function is called
    support_ml_app.set_initial_params(ml_model_name, ml_model, ml_model_config['n_classes'], x_train.shape[1])

    # Apply received parameters
    params = msg.content["arrays"].to_numpy_ndarrays()
    support_ml_app.set_model_params(ml_model_name, ml_model, params)

    # Train the model on local data
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ml_model.fit(x_train, y_train)

    # Extract the trained model parameters
    params_trained = support_ml_app.get_model_params(ml_model_name, ml_model)
    model_record = ArrayRecord(params_trained)

    # Prepare metrics
    if ml_model_name == 'LASSO' : regression = True
    else : regression = False
    metrics = support_ml_app.compute_metrics(y_train, ml_model.predict(x_train), regression = regression)
    metrics['num-examples'] = len(x_train)
    metric_record = MetricRecord(metrics)

    # Construct a Message with the results
    content = RecordDict({"arrays": model_record, "metrics": metric_record})

    # Save the model weights locally
    path_to_save_model = context.node_config['path_to_save_model'] if 'path_to_save_model' in context.node_config else './'
    os.makedirs(path_to_save_model, exist_ok = True)
    with open(f'{path_to_save_model}trained_params_{ml_model_name}_node_{node_id}.pkl', "wb") as f : pickle.dump(params, f)

    print(params_trained, "\n", metric_record)
    print("########################################################")

    return Message(content = content, reply_to = msg)

@app.query()
def query(msg : Message, context : Context) :
    """
    Send the weights of the trained model to the server.

    Implemented to obtain the model weights of a single nodes outside the FL process. From what I see the FedAvg strategy only return the finale model weights after the last round.
    For the PoC I also need the model weights of each node to show the difference between the models trained on different datasets.
    """
    
    # Get config
    node_id = context.node_config['partition-id']
    path_to_save_model = context.node_config['path_to_save_model'] if 'path_to_save_model' in context.node_config else './'
    my_config = msg.content['my_config']

    # Load the model weights
    ml_model_name = my_config['ml_model_name']
    with open(f"{path_to_save_model}/trained_params_{ml_model_name}_node_{node_id}.pkl", "rb") as f : params = pickle.load(f)
    
    model_weights = dict()
    if my_config['ml_model_name'] == 'SVM' :
        # For SVM the params are [coef, intercept], coef is of shape (n_classes, n_features)
        for i in range(len(params[0])) :
            model_weights[f'coef_class_{i}'] = list(params[0][i])

        model_weights['intercept'] = list(params[1])
    elif my_config['ml_model_name'] == 'LASSO' :
        model_weights['coef'] = list(params[0])
        model_weights['intercept'] = list(params[1])

    # Prepare the Message to send the model weights to the server
    model_record = MetricRecord(model_weights)
    reply_content = RecordDict({"query_results": model_record})
    # reply_content = RecordDict({"query_results": MetricRecord(query_results)})

    return Message(content = reply_content, reply_to = msg)

@app.evaluate()
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

