"""
A Flower `ServerApp` that constructs a histogram from clients data.

The computation is performed in two rounds :
- Round 0 : the server sends a message to the clients, asking them to compute the local min and max of the variable of interest. The server then computes the global min and max, which will be used to create the bins for the histogram (Note that this round can be skipped if the min and max are predefined in the server config file).
- Round 1 : the server sends a message to the clients, asking them to compute the local histogram of the variable of interest, using the bins computed in round 0. The server then sums the local histograms to obtain the final histogram.

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
import time
import toml

from collections.abc import Iterable
from logging import INFO

from flwr.common import Context, Message, MessageType, RecordDict, ConfigRecord
from flwr.common.logger import log
from flwr.server import Grid, ServerApp

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Flower ServerApp

app = ServerApp()

@app.main()
def main(grid: Grid, context: Context) -> None:
    """
    This `ServerApp` compute the centroids for k-means clustering
    """

    path_server_config = context.run_config['path_server_config'] if 'path_server_config' in context.run_config else './server_config.toml'
    server_config = toml.load(path_server_config)

    check_config(server_config)

    # Federation settings
    # min_nodes specify the minimum number of nodes required to start the histogram computation. If not specified, it is set to n_nodes (the total number of nodes connected to the grid).
    # max_number_of_attempts specify the maximum number of attempts to send the messages and receive the results from the clients. If not specified, it is set to 10. If this number is reached, an exception is raised.
    min_nodes              = server_config['min_nodes'] if 'min_nodes' in server_config else server_config['n_nodes']
    max_number_of_attempts = server_config['max_number_of_attempts'] if 'max_number_of_attempts' in server_config else 10
    path_to_save           = server_config['path_to_save'] if 'path_to_save' in server_config else './results/'
    
    # Dictionary used to communicate with the clients
    my_config = dict(
        current_round = -1,
        n_clusters = server_config['n_clusters'],
        max_local_iterations = server_config['max_local_iterations'],
        centroids = server_config['centroids']
    )

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    for i in range(server_config['n_rounds']) :
        log(INFO, "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        log(INFO, f"START ROUND {i}")

        # Update config for the current round
        my_config['current_round'] = i

        # Get all node ids
        # Note that this id will be used for all rounds, so it is not necessary to call this function again in the next rounds.
        node_ids_round = get_node_ids(grid, min_nodes)

        # Get the results from the clients
        results = get_data_from_clients(grid, node_ids_round, my_config, max_number_of_attempts)

        # Process results and save them
        save_results(results, path_to_save, i)

        log(INFO, f"END ROUND {i}")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Generic functions

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

def send_and_receive_data(grid: Grid, node_ids: list[int], server_round: int, my_config : dict = None) :
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

def get_data_from_clients(grid: Grid, node_ids : list[int], my_config : dict = None, max_number_of_attempts : int = 10) -> list[Message]:
    """
    Use the function `send_and_receive_data` to send messages to the clients and receive their results.
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
        results = send_and_receive_data(grid, node_ids, server_round = 0, my_config = my_config)

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

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_config(server_config : dict) -> None :
    """
    Check the server configuration and raise an exception if it is not valid.
    """

    if 'n_rounds' not in server_config :
        raise ValueError("n_rounds not specified in server config file. This parameter is required.")
    elif not isinstance(server_config['n_rounds'], int) or server_config['n_rounds'] <= 0 :
        raise ValueError(f"Invalid value for n_rounds in server config file. Expected a positive integer, got {server_config['n_rounds']}")

    if 'n_clusters' not in server_config :
        server_config['n_clusters'] = 8
        print(f"n_clusters not specified in server config file. Using sklear default value : {server_config['n_clusters']}")
    elif not isinstance(server_config['n_clusters'], int) or server_config['n_clusters'] <= 0 :
        raise ValueError(f"Invalid value for n_clusters in server config file. Expected a positive integer, got {server_config['n_clusters']}")

    if 'max_local_iterations' not in server_config :
        server_config['max_local_iterations'] = 300
        print(f"max_local_iterations not specified in server config file. Using sklearn default value : {server_config['max_local_iterations']}")
    elif not isinstance(server_config['max_local_iterations'], int) or server_config['max_local_iterations'] <= 0 :
        raise ValueError(f"Invalid value for max_local_iterations in server config file. Expected a positive integer, got {server_config['max_local_iterations']}")

    if 'centroids' not in server_config :
        server_config['centroids'] = None
        print(f"centroids not specified in server config file. Using random initialization")
    else :
        try :
            centroids = np.array(server_config['centroids'])
        except Exception as e:
            raise ValueError(f"Invalid value for centroids in server config file. Try to convert it to a numpy array but failed.\nERROR:\n{e}")

def save_results() -> None :
    """
    TODO
    """

