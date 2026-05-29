"""
Support functions for FL apps.

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

# Full package imports
import time

# Specific imports
from logging import INFO

# Flower imports
from flwr.common import Message, MessageType, RecordDict, ConfigRecord
from flwr.common.logger import log
from flwr.server import Grid

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Network functions

def get_node_ids(grid: Grid, min_nodes: int) -> list[int]:
    """
    Loop and wait until enough nodes are available.
    N.b. this is not a predefined flower function, but a custom function implemented for this app.

    Parameters
    ----------
    grid : Grid
        The Flower Grid instance.
        See https://flower.ai/docs/framework/ref-api/flwr.serverapp.Grid.html for more details.
    min_nodes : int
        Minimum number of nodes required.

    Returns
    -------
    list[int]
        List of all node ids.
    """
    
    # List for storing all node ids
    all_node_ids : list[int] = []

    # Loop until enough nodes are available
    while len(all_node_ids) < min_nodes:
        # Fetch all node ids
        all_node_ids = list(grid.get_node_ids())

        # If enough nodes are available, break the loop
        if len(all_node_ids) >= min_nodes:
            break

        # If not enough nodes are available, wait and try again
        log(INFO, "Waiting for nodes to connect...")
        time.sleep(2)

    return all_node_ids

def send_and_receive_data_through_query(grid: Grid, node_ids: list[int], server_round: int, my_config : dict = None) :
    """
    Send messages to the specified node ids and wait for all results using the Flower Message API.
    N.b. this is not a predefined flower function, but a custom function implemented for this app.

    Parameters
    ----------
    grid : Grid
        The Flower Grid instance.
        See https://flower.ai/docs/framework/ref-api/flwr.serverapp.Grid.html for more details.
    node_ids : list[int]
        List of node ids to which send the messages.
    server_round : int
        The current server round.
    my_config : dict, optional
        Dictionary containing personal configuration to be sent to the clients, by default None.
        If None, an empty dictionary will be sent.

    Returns
    -------
    replies : list[Message] | None
        The results obtained from the clients. They are instances of the Message class.
        See https://flower.ai/docs/framework/ref-api/flwr.common.Message.html for more details about the Message class.
        If an error occurred, None is returned.
    """
    
    # Create messages
    messages = []
    
    # Add other information to message
    recorddict = RecordDict()

    # Add personal configuration to message
    if my_config is not None : recorddict['my_config'] = ConfigRecord(my_config)
    # recorddict['my_config'] = ConfigRecord(my_config if my_config is not None else {})

    for node_id in node_ids:  # one message for each node
        message = Message(
            content = recorddict,
            message_type = MessageType.QUERY,
            dst_node_id = node_id,
            group_id = str(server_round),
        )

        messages.append(message)

        # Some notes about the Message class
        # The message_type can be one of the following : EVALUATE, QUERY, SYSTEM, TRAIN. Based on the type used, a different method will be called in the client.
        # In this case we use QUERY, so the `query` method in ClientApp will be called (With the decorator implementation, it is the function decorated with @app.query).
        # The group_id is used to group messages. In some settings, this is used as the federated learning round.
        # From flower documentation : "The ID of the group to which this message is associated. In some settings, this is used as the federated learning round"

    # Send messages and wait for all results
    replies = grid.send_and_receive(messages)
    log(INFO, "Received %s/%s results", len(replies), len(messages))
    
    # Check for errors
    for rep in replies :
        if rep.has_error():
            return None

    return replies

def get_data_from_clients_through_query(grid: Grid, node_ids : list[int], my_config : dict = None, max_number_of_attempts : int = 10) -> list[Message]:
    """
    Use the function `send_and_receive_data_through_query` to send messages to the clients and receive their results.
    If an error occurs, the function will retry until the maximum number of attempts is reached.
    Note that the function is "generic", in the sense that it can be used to send and receive any kind of data from the clients, granted that the data are in a format suitable for Flower messages.
    N.b. this is not a predefined flower function, but a custom function implemented for this app.

    Parameters
    grid : Grid
        The Flower Grid instance.
        See https://flower.ai/docs/framework/ref-api/flwr.serverapp.Grid.html for more details.
    node_ids : list[int]
        List of node ids to which send the messages.
    my_config : dict, optional
        Dictionary containing personal configuration to be sent to the clients, by default None.
        If None, an empty dictionary will be sent.
    max_number_of_attempts : int, optional
        Maximum number of attempts to send the messages and receive the results, by default 10.

    Returns
    -------
    results : list[Message]
        The results obtained from the clients. They are instances of the Message class.
        See https://flower.ai/docs/framework/ref-api/flwr.common.Message.html for more details about the Message class.
    """

    n_attempts = 0
    while (True) :
        results = send_and_receive_data_through_query(grid, node_ids, server_round = 0, my_config = my_config)

        if results is not None :
            # If no error, break the loop
            break
        else :
            n_attempts += 1
            log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
            if n_attempts >= max_number_of_attempts :
                raise Exception(f"Error in receiving data from clients during round {my_config['server_round']}. Maximum number of attempts ({max_number_of_attempts}) reached")
            time.sleep(2)

    return results
