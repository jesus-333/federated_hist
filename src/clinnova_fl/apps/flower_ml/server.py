from __future__ import annotations

import os
import pickle
import time
from pathlib import Path
from logging import INFO

import numpy as np
import toml
from flwr.common import ArrayRecord, ConfigRecord, Context, Message, MessageType, RecordDict
from flwr.common.logger import log
from flwr.server import Grid, ServerApp
from flwr.serverapp import strategy

from clinnova_fl.core.config import config_path
from clinnova_fl.core.data import get_ml_data, read_txt_list
from clinnova_fl.core.models import deserialize_model_weights, get_ml_model, get_model_params, set_initial_params, set_model_params

app = ServerApp()


@app.main()
def main(grid: Grid, context: Context) -> None:
    path_server_config = Path(context.run_config.get("path_server_config", config_path("server_config_ml.toml")))
    server_config = toml.load(path_server_config)
    fields_to_use_for_train = read_txt_list(server_config["path_file_with_fields_to_use_for_the_train"])
    x_server, y_server, _ = get_ml_data(server_config["path_server_data"], fields_to_use_for_train)
    path_to_save = Path(server_config.get("path_to_save", "./results/"))

    my_config = dict(server_config["ml_algorithm_config"])
    my_config["ml_model_name"] = server_config["ml_model_name"]
    my_config["fields_to_use_for_the_train"] = fields_to_use_for_train

    ml_model = get_ml_model(my_config["ml_model_name"], my_config)
    log(INFO, f"ML Model created: {ml_model}")
    set_initial_params(my_config["ml_model_name"], ml_model, 3, x_server.shape[1])
    arrays = ArrayRecord(get_model_params(my_config["ml_model_name"], ml_model))
    fl_strategy = strategy.FedAvg()
    train_config = ConfigRecord(config_dict={"config": my_config})
    result = fl_strategy.start(grid=grid, initial_arrays=arrays, num_rounds=server_config["num_rounds"], train_config=train_config)

    params_final = result.arrays.to_numpy_ndarrays()
    set_model_params(my_config["ml_model_name"], ml_model, params_final)

    path_to_save.mkdir(parents=True, exist_ok=True)
    with open(path_to_save / f"final_params_{my_config['ml_model_name']}.pkl", "wb") as f:
        pickle.dump(params_final, f)

    n_nodes = server_config["n_nodes"]
    node_ids = get_node_ids(grid, n_nodes)
    list_params_per_node = get_model_weights_from_clients(grid, node_ids, my_config)
    for i in range(n_nodes):
        with open(path_to_save / f"trained_params_{my_config['ml_model_name']}_node_{node_ids[i]}.pkl", "wb") as f:
            pickle.dump(list_params_per_node[i], f)


def get_node_ids(grid: Grid, min_nodes: int) -> list[int]:
    all_node_ids: list[int] = []
    while len(all_node_ids) < min_nodes:
        all_node_ids = list(grid.get_node_ids())
        if len(all_node_ids) >= min_nodes:
            break
        log(INFO, "Waiting for nodes to connect...")
        time.sleep(2)
    return all_node_ids


def send_and_receive_data(grid: Grid, node_ids: list[int], server_round: int, my_config: dict | None = None):
    messages = []
    record_dict = RecordDict()
    if my_config is not None:
        record_dict["my_config"] = ConfigRecord(my_config)
    for node_id in node_ids:
        messages.append(Message(content=record_dict, message_type=MessageType.QUERY, dst_node_id=node_id, group_id=str(server_round)))
    replies = grid.send_and_receive(messages)
    log(INFO, "Received %s/%s results", len(replies), len(messages))
    for rep in replies:
        if rep.has_error():
            return None
    return replies


def get_model_weights_from_clients(grid: Grid, node_ids: list[int], my_config: dict | None = None, max_number_of_attempts: int = 10) -> list:
    n_attempts = 0
    while True:
        results = send_and_receive_data(grid, node_ids, server_round=0, my_config=my_config)
        if results is not None:
            break
        n_attempts += 1
        log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
        if n_attempts >= max_number_of_attempts:
            raise Exception(f"Error in receiving data from clients. Maximum number of attempts ({max_number_of_attempts}) reached")
        time.sleep(2)

    list_params_per_node = []
    for rep in results:
        query_results = rep.content["query_results"]
        list_params_per_node.append(deserialize_model_weights(my_config["ml_model_name"], query_results))
    return list_params_per_node
