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
    custom_config, node_config = get_experiment_and_node_config(msg, context)

    # Get the data connector
    data_connector = generic.get_dataset(custom_config, node_config)

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

    # Get the experiment and node configuration
    custom_config, node_config = get_experiment_and_node_config(msg, context)

    # Get the data connector
    data_connector = generic.get_dataset(custom_config, node_config)
    
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
    custom_config, node_config = get_experiment_and_node_config(msg, context)

    # Get the data connector
    data_connector = generic.get_dataset(custom_config, node_config)

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
    custom_config : dict
        The custom configuration extracted from the message content.
        For more information about the custom_config, see the docstring of the :func:`~clinnova_fl.apps.support_fl.send_and_receive_data` and :func:`~clinnova_fl.apps.support_fl.get_data_from_clients` functions in :mod:`~clinnova_fl.apps.support_fl`.
    node_config : dict
        The node configuration, later used by the function get_dataset to create the data connector and the dataset.
    """

    # Get all the experiment config (from the message)
    custom_config = msg.content.config_records["custom_config"] if "custom_config" in msg.content.config_records else dict()

    # Get the node config (used for data connector and dataset creation)
    if 'simulation' in custom_config :
        node_config = get_simulated_node_config(context, custom_config) if custom_config['simulation'] else dict()
    elif 'run_with_nvflare' in custom_config :
        node_config = get_nvflare_node_config() if custom_config['run_with_nvflare'] else dict()
    else :
        node_config = context.node_config

    return custom_config, node_config

    # Note on context.node_config
    # Note that (at the time of writing 02/06/2026) the context.node_config can have custom values only if I created directly the supernode with the flower-supernode command, passing the custom node config as an argument of the command.
    # Otherwise, for simulation I think it's empty (but still even if it has some values you cannot customize it).
    # So for simulation, I had to add a method that create a "fake node config" dictionary
    
    # Old comment
    # Remember that the node config is passed as an argument of flower-supernode command.
    # So I can customize it only if I created directly the supernode with the flower-supernode command
    # For an example see https://flower.ai/docs/framework/how-to-run-flower-with-deployment-engine.html#start-two-flower-supernodes

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# The position of these two functions could be modified in the future

def get_simulated_node_config(context : Context, custom_config : dict) -> dict :
    """
    Create a "fake" node_config dictionary used for simulation. 
    In case of simulation I expect that the experiment config also contains the path for the simulated nodes configuration file.

    For now the function is simple but I prefer to keep it as a separate function in case I need to update it in the future.
    """
    
    # Get node id
    import pprint
    pprint.pprint(context)
    node_id = context.node_config['partition-id']

    if 'paths_nodes_config' not in custom_config :
        error_message = ""
        error_message += "ERROR : paths_nodes_config key is missing the the dictionary received in the client."
        error_message += f"\nCurrently, the keys in the dictionary are : {"\n- " + "\n- ".join(custom_config.keys())}"
        error_message += "\nThis key is required to run the app in simulation mode, as it contains the paths for the node configuration files."
        raise ValueError(error_message)

    print("QUESTO CUSTOM CONFIG ")
    pprint.pprint(custom_config)
    print("QUESTO e' CONTEXT")
    pprint.pprint(context )
    
    # Get the path for the node config and load it
    # TODO Convert to Path object
    path_node_config = custom_config['paths_nodes_config'][node_id]

    # Load the config
    node_config = toml.load(path_node_config)

    return node_config

def get_nvflare_node_config() -> dict :
    return dict()

