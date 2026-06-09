"""
Manage the interaction with csv files

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

import numpy as np
import pandas as pd

import clinnova_fl.config.connector.csv as config
from clinnova_fl.data_connector.generic import data_connector as generic_data_connector

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class data_connector(generic_data_connector):
    """
    Data connector for CSV files.
    
    This connector retrieves data from CSV files with optional filtering capabilities.
    See the docstring of :class:`~clinnova_fl.config.connector.csv.csv_connector_config`for the configuration options.
    
    Attributes
    ----------
    modality : str
        The data source type, always set to 'csv'.
    config : csv_connector_config
        Configuration for the CSV connector.
    
    Examples
    --------
    TODO 
    
    """

    def __init__(self, config : config.csv_connector_config) -> None:
        """
        Initialize the CSV data connector.
        
        Parameters
        ----------
        config : csv_connector_config
            The configuration object for this connector.
        """
        super().__init__(config)

        # Save the config
        self.config : config.csv_connector_config = config

        # Load the dataset
        # Note that from a security perspective, loading a csv file here and keep it as an attribute can be consider not ideal.
        # Loading on the fly inside the __get_item__ method would be more secure, but it would also be less efficient.
        # For now it is here because all of this is a prototype, but this kind of security issues should be discussed and addressed in the future.
        self.data = pd.read_csv(self.config.file_path)

    def __get_item__(self, idx) :
        """
        Return the row(s) specified by idx. The value of idx can be an integer index, a list of integer indices, a slice object (or any other type of index supported by pandas iloc).
        """

        return self.data.iloc[idx].to_numpy()

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

        return self.data[feature_name].to_numpy()

    def get_filtered_keys(self, feature : str, comparison_type : str, filter_value) -> np.ndarray :
        """
        Return the keys of the samples that satisfy the specified filter condition based on a feature value.

        Parameters
        ----------
        feature : str
            The name of the feature to use for filtering.
        comparison_type : str
            The type of comparison to perform. Supported values are: 'equals', 'less_than', 'greater_than', 'less_than_or_equal_to', 'greater_than_or_equal_to'.
        filter_value
            The value to compare the feature values against for filtering.

        Returns
        -------
        np.ndarray
            A numpy array containing the indices of the samples that satisfy the specified filter condition.
        """

        if feature not in self.data.columns : raise ValueError(f"Feature '{feature}' not found in the dataset. Available features are: {self.data.columns.tolist()}")

        return super().compare_numerical_features(feature, comparison_type, filter_value)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
