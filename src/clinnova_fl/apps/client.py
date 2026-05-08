"""
A generic wrapper for the ClientApp class, which is used to call the specific client-side application based on the configuration file received as input.
Based on the configuration file received as input a different server-side application will be used.

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>

"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Flower imports
from flwr.client import ClientApp
from flwr.common import Context, Message, MetricRecord, RecordDict

# Internal imports
from clinnova_fl import apps

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Flower ClientApp
app = ClientApp()

@app.query()
def query(msg : Message, context : Context) :
    """
    Call the specific client-side application based on the configuration file received as input.
    """

    if context.run_config["app"] == "flower_hist" :
        from clinnova_fl.apps.flower_hist.client import query
        return query(msg, context)
    elif context.run_config["app"] == "flower_ml" :
        raise NotImplementedError("The 'flower_ml' app does not have a 'query' function. Use the 'train' function instead.")
    elif context.run_config["app"] == "flower_k_means" :
        pass
    else :
        raise ValueError(f"Invalid app specified in the server configuration file: {context.run_config['app']}. Valid options are: {apps.LIST_OF_APPS}")
