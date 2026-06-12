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

    Note that the csv file should contain only numerical values. The only exception are :
    - The first row, which should contain the column names (i.e. the feature names).
    - The first column, which could contain the sample id. If detected, the sample id column is removed from the dataset and stored as a separate array.
    
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
        self.data = pd.read_csv(self.config.file_path, header = 0)

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Check if the first column contains the sample id. The check is done by checking if the first column is named 'id' or 'sample_id' (case insensitive). 
        # If the first column is detected as sample id, it is removed from the dataset and stored as a separate array.

        if self.data.columns[0].lower() in ['id', 'sample_id'] :
            self.sample_ids = self.data.iloc[:, 0].to_numpy()
            self.data = self.data.iloc[:, 1:]
        else :
            self.sample_ids = None

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        # Check that all the values in the dataset are numerical. If not, raise an error.

        if not np.issubdtype(self.data.dtypes.values, np.number).all() :
            non_numerical_columns = self.data.columns[~np.issubdtype(self.data.dtypes.values, np.number)]
            raise ValueError(f"All values in the dataset should be numerical. The following columns contain non-numerical values: {non_numerical_columns.tolist()}")

        # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        self.set_labels()

    def __get_item__(self, idx) :
        """
        Return the row(s) specified by idx. The value of idx can be an integer index, a list of integer indices, a slice object (or any other type of index supported by pandas iloc).
        """

        return self.data.iloc[idx].to_numpy()

    def set_labels(self) :
        """
        Set the labels. The labels are created only if the key feature_to_predict is specified in the configuration. If the feature_to_predict is not specified or set to None, the labels are set to None.

        If the feature_to_predict is specified, that column is removed from the data and set as the labels. Note that the labels should be saved as integers with values from 0 to n_classes - 1, where n_classes is the number of unique values in the feature_to_predict column.
        """

        if self.config.feature_to_predict is not None :
            # Check that the feature_to_predict is in the dataset
            if self.config.feature_to_predict not in self.data.columns : raise ValueError(f"Feature to predict '{self.config.feature_to_predict}' not found in the dataset. Available features are: {self.data.columns.tolist()}")
            
            # Create the labels by encoding the values in the feature_to_predict column as integers from 0 to n_classes - 1, where n_classes is the number of unique values in that column.
            self.labels = self.data[self.config.feature_to_predict].astype('category').cat.codes.to_numpy()

            # Check if there are negative values in the labels. 
            # Technically, this should happend only if features_to_predict contains missing/nan values which the previous line of code should encode as -1
            if (self.labels < 0).any() :
                idx_negative_labels = np.where(self.labels < 0)[0]
                raise ValueError(f"Find negative values in the labels at positions {idx_negative_labels}. Check the column '{self.config.feature_to_predict}' for missing/nan values, which are encoded as -1 in the labels.")
            
            # Remove the feature_to_predict column from the dataset
            self.data = self.data.drop(columns = [self.config.feature_to_predict])

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
