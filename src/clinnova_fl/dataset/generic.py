"""
Generic dataset base class

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

# General imports
from abc import ABC, abstractmethod
import toml

# Flower imports
from flwr.common import Context, Message

# Internal imports
from clinnova_fl.data_connector.generic import data_connector
from clinnova_fl.config.connector import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class dataset(ABC):
    """
    Abstract base class for all data the dataset.
    """

    # Note : Implementing the __get_item__ and __len__ methods allows to use the dataset with a torch DataLoader, which is a common pattern in PyTorch for loading data in batches.

    def __init__(self, dataset_id : str, data_connector : data_connector) :
        """
        Initialize the generic data connector with a configuration.
        
        Parameters
        ----------
        config : generic_connector_config
            The configuration object for this connector.
        """

        self.dataset_id = dataset_id
        self.data_connector = data_connector
    
    def __get_item__(self, key) :
        """
        Return the sample specified by the key.

        Returns
        -------
        sample(s)
                The sample specified by the key. The specific format of the returned sample(s) depends on the implementation of the data connector and the dataset.
        """

        return self.data_connector[key]

    def __len__(self) -> int :
        """
        Return the number of samples in the dataset

        Returns
        -------
        int
            The number of samples in the dataset, as determined by the length property of the data connector.
        """

        return len(self.data_connector)
    
    @abstractmethod
    def get_feature(self, feature : str) :
        """
        Get all the sample with a specific feature from the dataset.

        Note that not all the dataset may support this method, and it is up to the specific implementation to decide how to handle it (e.g., by raising an exception if not supported).
        """

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_dataset(experiment_config : dict, node_config : dict) -> dataset :
    """
    Get the dataset specified in the experiment configuration.

    Parameters
    ----------
    experiment_config : dict
        The configuration of the experiment, which should include a 'dataset_id' key specifying the id of the dataset to use.
    node_config : dict
        The configuration of the node, which is used to initialize the data connector for the dataset.
        It must be a dictionary where the keys are the dataset idx and the values are the path to toml file containing the configuration for the data connector of that dataset.
    """

    # Note. For now I save each dataset connector config in a toml file because it is a easy solution. In future this structure of the node config may be changed due to security reasons.

    # Get the id of the datset you want to use
    dataset_id = experiment_config['dataset_id']

    # Get the path to the toml file containing the configuration for the data connector of the dataset and load it
    data_connector_config_path = node_config['dataset_connectors'][dataset_id]
    data_connector_config_dict = toml.load(data_connector_config_path)

    # Convert the dictionary to a data connector configuration object
    data_connector_config = generic.get_connector_config(data_connector_config_dict)

    # Get the data connector 
    data_connector = generic.get_connector(data_connector_config)


