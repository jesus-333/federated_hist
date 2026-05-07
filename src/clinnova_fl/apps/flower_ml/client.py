from __future__ import annotations

import os
import pickle
import warnings
from pathlib import Path

from flwr.client import ClientApp
from flwr.common import ArrayRecord, Context, Message, MetricRecord, RecordDict

from clinnova_fl.core.config import data_path
from clinnova_fl.core.data import get_ml_data
from clinnova_fl.core.models import (
    compute_metrics,
    deserialize_model_weights,
    get_ml_model,
    get_model_params,
    serialize_model_weights,
    set_initial_params,
    set_model_params,
)

app = ClientApp()


@app.train()
def train(msg: Message, context: Context):
    node_id = context.node_config["partition-id"]
    path_client_data = Path(context.node_config.get("path_client_data", data_path(f"client_{node_id}_data_D1.csv")))
    ml_model_config = msg.content["config"]
    ml_model_name = ml_model_config["ml_model_name"]

    x_train, y_train, _ = get_ml_data(path_client_data, ml_model_config["fields_to_use_for_the_train"])
    ml_model = get_ml_model(ml_model_name, ml_model_config)
    set_initial_params(ml_model_name, ml_model, 3, x_train.shape[1])

    params = msg.content["arrays"].to_numpy_ndarrays()
    set_model_params(ml_model_name, ml_model, params)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ml_model.fit(x_train, y_train)

    params_trained = get_model_params(ml_model_name, ml_model)
    model_record = ArrayRecord(params_trained)
    regression = ml_model_name == "LASSO"
    metrics = compute_metrics(y_train, ml_model.predict(x_train), regression=regression)
    metrics["num-examples"] = len(x_train)
    metric_record = MetricRecord(metrics)
    content = RecordDict({"arrays": model_record, "metrics": metric_record})

    path_to_save_model = Path(context.node_config.get("path_to_save_model", "./"))
    path_to_save_model.mkdir(parents=True, exist_ok=True)
    with open(path_to_save_model / f"trained_params_{ml_model_name}_node_{node_id}.pkl", "wb") as f:
        pickle.dump(params, f)

    return Message(content=content, reply_to=msg)


@app.query()
def query(msg: Message, context: Context):
    node_id = context.node_config["partition-id"]
    path_to_save_model = Path(context.node_config.get("path_to_save_model", "./"))
    my_config = msg.content["my_config"]
    ml_model_name = my_config["ml_model_name"]

    with open(path_to_save_model / f"trained_params_{ml_model_name}_node_{node_id}.pkl", "rb") as f:
        params = pickle.load(f)

    model_weights = serialize_model_weights(ml_model_name, params)
    model_record = MetricRecord(model_weights)
    reply_content = RecordDict({"query_results": model_record})
    return Message(content=reply_content, reply_to=msg)


@app.evaluate()
def evaluate(message: Message, context: Context) -> Message:
    metric_record = MetricRecord({"mse": 1.0, "mae": 1.0, "num-examples": 42})
    content = RecordDict({"metrics": metric_record})
    return Message(content, reply_to=message)
