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

def get_node_ids(grid: Grid, min_nodes: int, max_number_of_attempts : int = 10) -> list[int]:
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
        If set to a number greater than 1 the function will loop and wait until at least that number of nodes are available.
        Otherwise, if set to 1, the function will return as soon as at least one node is available (i.e. return all the nodes that you find at the moment, without waiting for more nodes to connect).
    max_number_of_attempts : int, optional
        Maximum number of attempts to check for available nodes, by default 10.
        If the maximum number of attempts is reached and there are still not enough nodes available, an exception is raised.

    Returns
    -------
    list[int]
        List of all node ids.
    """

    if min_nodes <= 0 : raise ValueError(f"min_nodes must be greater than 0. Current value is {min_nodes}")
    
    # List for storing all node ids
    all_node_ids : list[int] = []

    # Loop until enough nodes are available
    for i in range(max_number_of_attempts) :
        # Fetch all node ids
        all_node_ids = list(grid.get_node_ids())

        # If enough nodes are available, break the loop
        if len(all_node_ids) >= min_nodes:
            break

        # If not enough nodes are available, wait and try again
        log(INFO, "Waiting for nodes to connect...")
        time.sleep(2)

    if len(all_node_ids) < min_nodes : raise Exception(f"Not enough nodes available. Minimum required is {min_nodes}, but only {len(all_node_ids)} are available after {max_number_of_attempts} attempts.")

    return all_node_ids

def send_and_receive_data(message_type : MessageType, grid: Grid, node_ids: list[int], server_round: int, custom_config : dict = None) :
    """
    Send messages to the specified node ids and wait for all results using the Flower Message API.
    N.b. this is not a predefined flower function, but a custom function implemented for this app.

    Parameters
    ----------
    message_type : MessageType
        The type of the message to be sent. It can be one of the following : EVALUATE, QUERY, and  TRAIN.
        Based on the type used, a different method will be called in the client.
    grid : Grid
        The Flower Grid instance.
        See https://flower.ai/docs/framework/ref-api/flwr.serverapp.Grid.html for more details.
    node_ids : list[int]
        List of node ids to which send the messages.
    custom_config : int
        The custom configuration to be sent to the clients. If None is passed, no custom configuration will be sent. Default is None.
        See the docstring of the `get_data_from_clients` function for more details about the custom configuration.
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
    if custom_config is not None : recorddict['custom_config'] = ConfigRecord(custom_config)
    # recorddict['my_config'] = ConfigRecord(my_config if my_config is not None else {})

    for node_id in node_ids:  # one message for each node
        message = Message(
            content = recorddict,
            message_type = message_type,
            dst_node_id = node_id,
            group_id = str(server_round),
        )

        messages.append(message)

        # Some notes about the Message class
        # The message_type can be one of the following : EVALUATE, QUERY, and  TRAIN. Based on the type used, a different method will be called in the client. (In past, I also write in this comment that exist SYSTEM message type but I think it was an error on my side)
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

def get_data_from_clients(message_type : MessageType, grid: Grid, node_ids : list[int], custom_config : dict = None, max_number_of_attempts : int = 10, sleep_time : int = 2) -> list[Message]:
    """
    Use the function `send_and_receive_data_through` to send messages to the clients and receive their results.
    If an error occurs, the function will retry until the maximum number of attempts is reached.
    Note that the function is "generic", in the sense that it can be used to send and receive any kind of data from the clients, granted that the data are in a format suitable for Flower messages.
    N.b. this is not a predefined flower function, but a custom function implemented for this app.

    Parameters
    ----------
    message_type : MessageType
        The type of the message to be sent. It can be one of the following : EVALUATE, QUERY, and  TRAIN.
        Based on the type used, a different method will be called in the client.
    grid : Grid
        The Flower Grid instance.
        See https://flower.ai/docs/framework/ref-api/flwr.serverapp.Grid.html for more details.
    node_ids : list[int]
        List of node ids to which send the messages.
    custom_config : dict, optional
        Dictionary containing personal configuration to be sent to the clients. By default None.
        If it is not None, the custom dictionary will be sent to the clients as part of the message content, under the key "custom_config". The clients can access it with `msg.content.config_records["custom_config"]` (where msg is the Message object received by the client).
        Note that if you pass a dictionary, not all datatype are supported by the Flower Message API. At the moment (06/26) the supported data types are : int | float | str | bytes | bool | list[int] | list[float] | list[str] | list[bytes] | list[bool]
    max_number_of_attempts : int, optional
        Maximum number of attempts to send the messages and receive the results, by default 10.
    sleep_time : int, optional
        Time to wait between complete attempts, expressed in seconds. By default 2 seconds.

    Returns
    -------
    results : list[Message]
        The results obtained from the clients. They are instances of the Message class.
        See https://flower.ai/docs/framework/ref-api/flwr.common.Message.html for more details about the Message class.
    """

    n_attempts = 0
    while (True) :
        results = send_and_receive_data(message_type, grid, node_ids, server_round = 0, custom_config = custom_config)

        if results is not None :
            # If no error, break the loop
            break
        else :
            n_attempts += 1
            log(INFO, f"Error in receiving data from clients. Attempt {n_attempts}/{max_number_of_attempts}")
            if n_attempts >= max_number_of_attempts :
                raise Exception(f"Error in receiving data from clients during round {n_attempts}. Maximum number of attempts ({max_number_of_attempts}) reached")
            time.sleep(sleep_time)

    return results

def check_custom_config(custom_config : dict) :
    """
    Check that the custom configuration contains only supported data types.
    """

    supported_data_types = (int, float, str, bytes, bool, list[int], list[float], list[str], list[bytes], list[bool])
    for key, value in custom_config.items() :
        if not isinstance(value, supported_data_types) :
            raise ValueError(f"Unsupported data type in custom configuration. Key: {key}, Value: {value}, Type of value: {type(value)}. Supported data types are {supported_data_types}")

