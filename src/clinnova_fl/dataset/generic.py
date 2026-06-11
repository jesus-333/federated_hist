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
from clinnova_fl.data_connector import generic as generic_data_connector
from clinnova_fl.config.connector import generic as generic_config
from clinnova_fl.dataset import EXISTING_DATASTE_TYPE

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class dataset(ABC):
    """
    Abstract base class for all data the dataset.
    """

    # Note : Implementing the __get_item__ and __len__ methods allows to use the dataset with a torch DataLoader, which is a common pattern in PyTorch for loading data in batches.

    def __init__(self, dataset_id : str, data_connector : generic_data_connector.data_connector) :
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
    
    # Get dataset information
    dataset_connector_config_file_path = node_config[dataset_id]['dataset_connector_config_file_path']
    dataset_type = node_config[dataset_id]['dataset_types']
    
    # Check if the dataset type is supported
    if dataset_type not in EXISTING_DATASTE_TYPE : raise ValueError(f"Dataset type {dataset_type} is not supported. Supported dataset types are: {EXISTING_DATASTE_TYPE}")

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Get the data connector

    # Load the data connector configuration from the toml file
    data_connector_config_dict = toml.load(dataset_connector_config_file_path)

    # Convert the dictionary to a data connector configuration object
    data_connector_config = generic_config.get_connector_config(data_connector_config_dict)

    # Create the data connector
    data_connector_object = generic_data_connector.get_connector(data_connector_config)

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Create the dataset
    
    dataset_class = get_dataset_class(dataset_type)
    dataset_istance = dataset_class(dataset_id = dataset_id, data_connector = data_connector_object)

    return dataset_istance


def get_dataset_class(dataset_type : str) -> dataset :
    """
    Get the dataset class for a specific dataset type. Keep as a separat function so it's easier to maintain and update the supported dataset types.

    Parameters
    ----------
    dataset_type : str
        The type of the dataset (e.g., 'tabular', 'images', etc.). Supported dataset types are defined in the EXISTING_DATASTE_TYPE list in the clinnova_fl.dataset.__init__.py module.
    """

    if dataset_type == "tabular" :
        from clinnova_fl.dataset.tabular import dataset as dataset_class
    elif dataset_type == "images" :
        from clinnova_fl.dataset.images import dataset as dataset_class

    return dataset_class
