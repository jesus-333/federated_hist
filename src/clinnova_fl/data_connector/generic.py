"""
Generic data connector base class

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

# General imports
from abc import ABC, abstractmethod
import numpy as np

# Internal imports
from clinnova_fl.config.connector import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class data_connector(ABC):
    """
    Abstract base class for all data connectors.
    
    This class provides a template for creating specific data connectors (e.g., CSV, JSON, database connectors).
    All connector classes should inherit from this class and implement the required abstract methods and properties.
    
    A data connector is responsible for retrieving data from a specific source (file, database, API, etc.)
    and providing it in a standardized format (numpy arrays).
    
    Attributes
    ----------
    modality : str
        The type of data source this connector handles (e.g., 'csv', 'json', 'database').
    config : generic_connector_config
        The configuration object for this connector.
    
    Methods
    -------
    get_data_array()
        Retrieve data as a 1D numpy array.
    get_data_matrix()
        Retrieve data as a 2D numpy array.
    """
    
    def __init__(self, config : generic.connector_config, node_config : dict = None) :
        """
        Initialize the generic data connector with a configuration.
        
        Parameters
        ----------
        config : generic_connector_config
            The configuration object for this connector.
        node_config : dict, optional
            Additional configuration that store information specific for the federated node (e.g. node_id, some key for authentication, etc.).
            This is optional because not all connectors may need it, but it can be useful for some connectors (e.g. database connectors that need authentication, or API connectors that need an API key).
        """

        self.modality = config.modality
        self.config = config
        self.node_config = node_config
    
    @abstractmethod
    def get_data_array(self) -> np.ndarray:
        """
        Get data as a 1D numpy array.
        
        This method must be implemented by all subclasses to retrieve data in array format
        based on the connector's configuration.
        
        Returns
        -------
        np.ndarray
            A 1D numpy array containing the extracted data.
        
        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.
        """

        raise NotImplementedError("Subclasses must implement get_data_array()")
    
    @abstractmethod
    def get_data_matrix(self) -> np.ndarray:
        """
        Get data as a 2D numpy array.
        
        This method must be implemented by all subclasses to retrieve data in matrix format
        based on the connector's configuration.
        
        Returns
        -------
        np.ndarray
            A 2D numpy array containing the extracted data.
        
        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.
        """

        raise NotImplementedError("Subclasses must implement get_data_matrix()")

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_connector(connector_config : generic.connector_config) -> data_connector :
    """
    Based on the config received, return the appropriate connector.
    """

    modality = connector_config.modality

    if modality == 'csv' :
        from clinnova_fl.data_connector.csv import data_connector
    else :
        raise ValueError(f'Modality {modality} not supported. Currently supported modalities are: {generic.SUPPORTED_MODALITY}')

    return data_connector(connector_config)




