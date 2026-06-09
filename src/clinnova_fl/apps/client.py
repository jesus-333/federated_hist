"""
A generic wrapper for the ClientApp class, which is used to call the specific client-side application based on the configuration file received as input.
Based on the configuration file received as input a different server-side application will be used.

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# General imports
import toml

# Flower imports
from flwr.client import ClientApp
from flwr.common import Context, Message

# Internal imports
from clinnova_fl import apps
from clinnova_fl.dataset import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Flower ClientApp
app = ClientApp()

@app.evaluate()
def evaluate(msg : Message, context : Context) :
    """
    Call the specific client-side evaluation function based on the configuration received.
    """
    
    # Get the experiment and node configuration
    experiment_config, node_config = get_experiment_and_node_config(msg, context)

    # Get the data connector
    data_connector = generic.get_dataset(experiment_config, node_config)

    # Get the evaluation function for the specified app
    if context.run_config["app"] == "flower_hist" :
        raise NotImplementedError("The 'flower_hist' app does not have an 'evaluate' function.")
    elif context.run_config["app"] == "flower_ml" :
        from clinnova_fl.apps.flower_ml.client import evaluate
    elif context.run_config["app"] == "flower_k_means" :
        pass
    else :
        raise ValueError(f"Invalid app specified in the server configuration file: {context.run_config['app']}. Valid options are: {apps.LIST_OF_APPS}")

    return evaluate(msg, context, data_connector)

@app.query()
def query(msg : Message, context : Context) :
    """
    Call the specific client-side query function based on the configuration received.
    """

    print("DEBUG TO REMOVE. INSIDE THE SERVER")
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
    print(context)
    import pprint
    pprint.pprint(context)
    pprint.pprint(msg)
    print("BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")

    # Get the experiment and node configuration
    experiment_config, node_config = get_experiment_and_node_config(msg, context)

    # Get the data connector
    data_connector = generic.get_dataset(experiment_config, node_config)
    
    # Get the query function for the specified app
    if context.run_config["app"] == "flower_hist" :
        from clinnova_fl.apps.flower_hist.client import query
    elif context.run_config["app"] == "flower_ml" :
        raise NotImplementedError("The 'flower_ml' app does not have a 'query' function. Use the 'train' function instead.")
    elif context.run_config["app"] == "flower_k_means" :
        pass
    else :
        raise ValueError(f"Invalid app specified in the server configuration file: {context.run_config['app']}. Valid options are: {apps.LIST_OF_APPS}")

    return query(msg, context, data_connector)

@app.train()
def train(msg : Message, context : Context) :
    """
    Call the specific client-side training function based on the configuration received.
    """

    # Get the experiment and node configuration
    experiment_config, node_config = get_experiment_and_node_config(msg, context)

    # Get the data connector
    data_connector = generic.get_dataset(experiment_config, node_config)

    # Get the training function for the speciefied app
    if context.run_config["app"] == "flower_hist" :
        raise NotImplementedError("The 'flower_hist' app does not have a 'train' function.")
    elif context.run_config["app"] == "flower_ml" :
        from clinnova_fl.apps.flower_ml.client import train
    elif context.run_config["app"] == "flower_k_means" :
        pass
    else :
        raise ValueError(f"Invalid app specified in the server configuration file: {context.run_config['app']}. Valid options are: {apps.LIST_OF_APPS}")

    return train(msg, context, data_connector)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_experiment_and_node_config(msg : Message, context : Context) -> tuple[dict, dict] :
    """
    Get the experiment and node configuration from the message and context.

    Parameters
    ----------
    msg : Message
        The message received by the client, which contains the experiment configuration in its content.
    context : Context
        The context of the client, which contains the node configuration in its node_config property.

    Returns
    -------
    experiment_config : dict
        The experiment configuration extracted from the message content.
    node_config : dict
        The node configuration, later used by the function get_dataset to create the data connector and the dataset.
    """

    # Get all the experiment config (from the message)
    experiment_config = msg.content.config_records["experiment_config"]

    # Get the node config (used for data connector and dataset creation)
    if experiment_config['simulation'] :
        node_config = get_simulated_node_config()
    elif experiment_config['run_with_nvflare'] :
        node_config = get_nvflare_node_config()
    else :
        node_config = context.node_config

    return experiment_config, node_config

    # Note on context.node_config
    # Note that (at the time of writing 02/06/2026) the context.node_config can have custom values only if I created directly the supernode with the flower-supernode command, passing the custom node config as an argument of the command.
    # Otherwise, for simulation I think it's empty (but still even if it has some values you cannot customize it).
    # So for simulation, I had to add a method that create a "fake node config" dictionary
    
    # Old comment
    # Remember that the node config is passed as an argument of flower-supernode command.
    # So I can customize it only if I created directly the supernode with the flower-supernode command
    # For an example see https://flower.ai/docs/framework/how-to-run-flower-with-deployment-engine.html#start-two-flower-supernodes

# TEMPORARY. TO BE REMOVED ONCE THE SIMULATION AND NVFLARE CONFIGS ARE DEFINED.
# Added only to remove the error 
def get_simulated_node_config() -> dict :
    return dict()

def get_nvflare_node_config() -> dict :
    return dict()
