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

from clinnova_fl.data_connector.generic import data_connector as generic_data_connector
from clinnova_fl.config.connector.synthetic import synthetic_connector_config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class data_connector(generic_data_connector):
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

        np.random.seed(self.config.seed)

        if self.config.distribution == 'normal':
            self.data = np.random.normal(loc = self.config.loc, scale = self.config.scale, size = self.config.size)
        elif self.config.distribution == 'uniform':
            self.data = np.random.uniform(low = self.config.low, high = self.config.high, size = self.config.size)
        else:
            raise ValueError(f"Distribution '{self.config.distribution}' not supported.")
        
        # Create preferix for the feature names. Use feature_1, feature_2, ..., feature_n for n features.
        if len(self.config.size) == 2 :
            # Note that features make sense only if the data is 2D.
            self.features = [f"feature_{i + 1}" for i in range(self.config.size[1])]
        else :
            self.features = None

    def __get_item__(self, idx) :
        """
        Return the row(s) specified by idx. The value of idx can be an integer index, a list of integer indices, a slice object (or any other type of index supported by pandas iloc).
        """

        return self.data[idx].to_numpy()

    def get_feature(self, feature_name : str) -> np.ndarray :
        """
        Get a specific feature from the dataset as a numpy array.

        Parameters
        ----------
        feature_name : str
            The name of the feature to retrieve.

        Returns
        -------
        np.ndarray
            A numpy array containing the values of the specified feature.
        """

        if self.features is None :
            raise ValueError("The data is not 2D, so features are not defined.")
        else :
            if feature_name not in self.features :
                raise ValueError(f"Feature '{feature_name}' not found. Available features are: {self.features}")
            else :
                feature_idx = self.features.index(feature_name)
                return self.data[:, feature_idx]

    def get_filtered_keys(self, feature : str, comparison_type : str, filter_value) -> np.ndarray :
        """
        Return the keys of the samples that satisfy the specified filter condition based on a feature value.
        """

        if self.features is None :
            raise ValueError("The data is not 2D, so features are not defined.")
        else :
            if feature not in self.features :
                raise ValueError(f"Feature '{feature}' not found. Available features are: {self.features}")
            else :
                return super().compare_numerical_features(feature, comparison_type, filter_value)




