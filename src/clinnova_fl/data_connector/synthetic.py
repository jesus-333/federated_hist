"""
synthetic data connector for generating synthetic data

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

import numpy as np

from clinnova_fl.data_connector.generic import generic_data_connector
from clinnova_fl.config.connector.synthetic import synthetic_connector_config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class synthetic_data_connector(generic_data_connector):
    """
    Data connector for generating synthetic synthetic data.
    
    This connector generates random data from different distributions for testing and debugging purposes.
    
    Attributes
    ----------
    modality : str
        Always set to 'synthetic'.
    config : synthetic_connector_config
        Configuration for the synthetic connector.
    
    Examples
    --------
    >>> config = synthetic_connector_config(distribution='normal', size=300, seed=123)
    >>> connector = synthetic_data_connector(config)
    >>> data = connector.get_data_array()
    """
    
    def __init__(self, config : synthetic_connector_config) -> None:
        """
        Initialize the synthetic data connector.
        
        Parameters
        ----------
        config : synthetic_connector_config
            The configuration object for this connector.
        """
        super().__init__(config)
        self.config : synthetic_connector_config = config
    
    def get_data_array(self) -> np.ndarray:
        """
        Generate synthetic data as a 1D numpy array.
        
        Returns
        -------
        np.ndarray
            A 1D numpy array containing synthetic data.
        """
        np.random.seed(self.config.seed)
        
        if self.config.distribution == 'normal':
            return np.random.normal(loc = self.config.loc, scale = self.config.scale, size = self.config.size_1D_array)
        elif self.config.distribution == 'uniform':
            return np.random.uniform(low = self.config.low, high = self.config.high, size = self.config.size_1D_array)
        else:
            raise ValueError(f"Distribution '{self.config.distribution}' not supported.")
    
    def get_data_matrix(self) -> np.ndarray:
        """
        Generate synthetic data as a 2D numpy array.
        
        Returns
        -------
        np.ndarray
            A 2D numpy array containing synthetic data (1 column).
        """

        # TODO
        raise NotImplementedError("get_data_matrix is not implemented yet.")
