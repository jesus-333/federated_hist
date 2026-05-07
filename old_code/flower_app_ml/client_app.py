"""
A Flower `ClientApp` that train a machine learning algorithm
Currently implemented algorithm are SVM

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
@date: September 2025
"""
import os
import pickle
import warnings

from flwr.client import ClientApp
from flwr.common import ArrayRecord, Context, Message, MetricRecord, RecordDict

import support_ml_app

app = ClientApp()

@app.train()
def train(msg: Message, context: Context):
    print("########################################################")
    import pathlib
    print(pathlib.Path().resolve(), "AAAAAAAAAAAAAAAAA\n")
    print(context)
    print("AAAAAAAAAAAAAAAAA")

    node_id = context.node_config['partition-id']
    path_client_data = f'../../../../data/client_{node_id}_data_D1.csv'

    ml_model_config = msg.content["config"]
    ml_model_name = ml_model_config['ml_model_name']

    x_train, y_train, _ = support_ml_app.get_data(path_client_data, ml_model_config['fields_to_use_for_the_train'])
    ml_model = support_ml_app.get_ml_model(ml_model_name, ml_model_config)
    support_ml_app.set_initial_params(ml_model_name, ml_model, 3, x_train.shape[1])
    params = msg.content["arrays"].to_numpy_ndarrays()
    support_ml_app.set_model_params(ml_model_name, ml_model, params)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ml_model.fit(x_train, y_train)

    params_trained = support_ml_app.get_model_params(ml_model_name, ml_model)
    model_record = ArrayRecord(params_trained)

    if ml_model_name == 'LASSO' : regression = True
    else : regression = False
    metrics = support_ml_app.compute_metrics(y_train, ml_model.predict(x_train), regression = regression)
    metrics['num-examples'] = len(x_train)
    metric_record = MetricRecord(metrics)

    content = RecordDict({"arrays": model_record, "metrics": metric_record})

    path_to_save_model = context.node_config['path_to_save_model'] if 'path_to_save_model' in context.node_config else './'
    os.makedirs(path_to_save_model, exist_ok = True)
    with open(f'{path_to_save_model}trained_params_{ml_model_name}_node_{node_id}.pkl', "wb") as f : pickle.dump(params, f)

    print(params_trained, "\n", metric_record)
    print("########################################################")

    return Message(content = content, reply_to = msg)

@app.query()
def query(msg : Message, context : Context) :
    node_id = context.node_config['partition-id']
    path_to_save_model = context.node_config['path_to_save_model'] if 'path_to_save_model' in context.node_config else './'
    my_config = msg.content['my_config']

    ml_model_name = my_config['ml_model_name']
    with open(f"{path_to_save_model}/trained_params_{ml_model_name}_node_{node_id}.pkl", "rb") as f : params = pickle.load(f)
    
    model_weights = dict()
    if my_config['ml_model_name'] == 'SVM' :
        for i in range(len(params[0])) :
            model_weights[f'coef_class_{i}'] = list(params[0][i])
        model_weights['intercept'] = list(params[1])
    elif my_config['ml_model_name'] == 'LASSO' :
        model_weights['coef'] = list(params[0])
        model_weights['intercept'] = list(params[1])

    model_record = MetricRecord(model_weights)
    reply_content = RecordDict({"query_results": model_record})
    return Message(content = reply_content, reply_to = msg)

@app.evaluate()
def evaluate(message: Message, context: Context) -> Message :
    metrics = {
        "mse": 1.0,
        "mae": 1.0,
        "num-examples": 42,
    }
    metric_record = MetricRecord(metrics)
    content = RecordDict({"metrics": metric_record})
    return Message(content, reply_to = message)
