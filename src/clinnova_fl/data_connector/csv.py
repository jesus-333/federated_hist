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
from clinnova_fl.data_connector.generic import generic_data_connector

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class data_connector(generic_data_connector):
    """
    Data connector for CSV files.
    
    This connector retrieves data from CSV files with optional filtering capabilities.
    See the docstring of :class:`~clinnova_fl.config.connector.csv.csv_connector_config` 
    for the configuration options, including filtering.
    
    Attributes
    ----------
    modality : str
        The data source type, always set to 'csv'.
    config : csv_connector_config
        Configuration for the CSV connector.
    
    Examples
    --------
    Basic usage without filtering:
    
    >>> connector_config = csv_connector_config(
    ...     file_path="data.csv",
    ...     field_name="age"
    ... )
    >>> connector = csv_data_connector(connector_config)
    >>> data = connector.get_data_array()
    
    With filtering:
    
    >>> connector_config = csv_connector_config(
    ...     file_path="data.csv",
    ...     field_name="age",
    ...     filter_field="country",
    ...     filter_type="equals",
    ...     filter_value="USA"
    ... )
    >>> connector = csv_data_connector(connector_config)
    >>> data = connector.get_data_array()
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
        self.config: config.csv_connector_config = config
    
    def get_data_array(self) -> np.ndarray:
        """
        Get an array of data from a csv file. The data are returned as a numpy array.

        Returns
        -------
        np.ndarray
            A numpy array containing the extracted data.
        """

        # Load the data and get the data
        dataset = pd.read_csv(self.config.file_path)
        data = dataset[self.config.field_name].to_numpy()
        
        # Check if filtering is needed
        if self.config.filter_field is not None:
            # Filtering required

            # Get the data for filtering and compute the indices of the rows to keep
            data_for_filtering = dataset[self.config.filter_field].to_numpy()
            idx_to_keep = None
            
            # Compute the indices of the rows to keep based on the filter type
            if self.config.filter_type == 'equals':
                idx_to_keep = data_for_filtering == self.config.filter_value
            elif self.config.filter_type == 'less_than':
                idx_to_keep = data_for_filtering < self.config.filter_value
            elif self.config.filter_type == 'greater_than':
                idx_to_keep = data_for_filtering > self.config.filter_value
            elif self.config.filter_type == 'less_than_or_equal_to':
                idx_to_keep = data_for_filtering <= self.config.filter_value
            elif self.config.filter_type == 'greater_than_or_equal_to':
                idx_to_keep = data_for_filtering >= self.config.filter_value
            else:
                raise ValueError(f"Filter type {self.config.filter_type} not supported. Supported filter types are: 'equals', 'less_than', 'greater_than', 'less_than_or_equal_to', 'greater_than_or_equal_to'.")
            
            # Filter and return the data
            return data[idx_to_keep]
        else:
            # Return directly all the data
            return data

    def get_data_matrix(self) -> np.ndarray:
        """
        Get a matrix of data from a csv file. The data are returned as a numpy array.

        Returns
        -------
        np.ndarray
            A 2D numpy array containing the extracted data.
        """

        # TODO
        raise NotImplementedError("get_data_matrix is not implemented yet.")
