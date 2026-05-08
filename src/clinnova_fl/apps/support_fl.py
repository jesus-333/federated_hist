"""Shared Flower server helpers

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

from __future__ import annotations

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import time
from logging import INFO

from flwr.common import ConfigRecord, Message, MessageType, RecordDict
from flwr.common.logger import log
from flwr.server import Grid

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Shared helpers

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
    recorddict = RecordDict()
    if my_config is not None:
        recorddict["my_config"] = ConfigRecord(my_config)
    for node_id in node_ids:
        messages.append(Message(content=recorddict, message_type=MessageType.QUERY, dst_node_id=node_id, group_id=str(server_round)))
    replies = grid.send_and_receive(messages)
    log(INFO, "Received %s/%s results", len(replies), len(messages))
    for rep in replies:
        if rep.has_error():
            return None
    return replies


def get_data_from_clients(grid: Grid, node_ids: list[int], my_config: dict | None = None, max_number_of_attempts: int = 10):
    n_attempts = 0
    while True:
        results = send_and_receive_data(grid, node_ids, server_round=0, my_config=my_config)
        if results is not None:
            break
        n_attempts += 1
        log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
        if n_attempts >= max_number_of_attempts:
            raise Exception(f"Error in receiving data from clients during round {my_config['server_round']}. Maximum number of attempts ({max_number_of_attempts}) reached")
        time.sleep(2)
    return results
