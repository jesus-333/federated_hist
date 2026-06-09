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
    get_sample()
        Retrieve a single sample from the data source.
    get_feature()
        Retrieve a single feature from the data source.
    """
    
    def __init__(self, config : generic.connector_config) :
        """
        Initialize the generic data connector with a configuration.
        
        Parameters
        ----------
        config : generic_connector_config
            The configuration object for this connector.
        """

        self.modality = config.modality
        self.config = config

        self.SUPPORTED_COMPARISON_TYPE = ['equals', 'not_equals', 'greater_than', 'less_than', 'less_than_or_equal', 'greater_than_or_equal']

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Abstract methods that must be implemented by all connectors

    @abstractmethod
    def __get_item__(self, key) :
        """
        Get the sample(s) specified by the key from the data source. The returned sample(s) and their format will depend on the specific implementation of the connector (e.g., a row from a CSV file, a record from a database, etc.).
        Note that the key can be a single identifier (e.g., an index, a primary key) or a more complex query depending on the data source and the connector implementation.

        Returns
        -------
        sample
            The data sample(s) retrieved from the data source. The format of the sample(s) will depend on the specific implementation of the connector.

        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.
        """

        raise NotImplementedError("Subclasses must implement this method.")

        # P.s. the __get_item__ method is a special method in Python that allows an object to use the square bracket notation (e.g., obj[key]) to retrieve items.
        # By defining this method as abstract, we ensure that any subclass of data_connector must implement it, allowing for consistent access to data samples across different types of connectors.

    @abstractmethod
    def __len__(self) -> int :
        """
        Return the number of samples in the data source. The returned value will depend on the specific implementation of the connector (e.g., the number of rows in a CSV file, the number of records in a database, etc.).

        Returns
        -------
        int
            The number of samples in the data source.

        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_feature(self, feature : str) :
        """
        Get a single feature from the data source (e.g. a column from a table, a field from a record, etc.).
        The returned feature and its format will depend on the specific implementation of the connector (e.g., a column from a CSV file, a field from a database, etc.).

        Note that not all the connectors may support this method, and it is up to the specific implementation to decide how to handle it (e.g., by raising an exception if not supported).

        Parameters
        ----------
        feature : str
            The identifier of the feature to retrieve. The specific format of the feature identifier will depend on the implementation of the connector (e.g., a column name for a CSV file, a field name for a database, etc.).

        Returns
        -------
        feature
            A single data feature retrieved from the data source. The format of the feature will depend on the specific implementation of the connector.

        Raises
        ------
        NotImplementedError
            If not implemented by a subclass.
        """

        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def get_filtered_keys(self, feature : str, comparison_type : str, filter_value) :
        """
        Return the keys of the samples that satisfy the specified filter condition based on a feature value.

        Note that not all the connectors may support this method, and it is up to the specific implementation to decide how to handle it (e.g., by raising an exception if not supported).
        The implementation of this method is necessary for the :meth:`filter_based_on_feature_value` method to work.
        """

    # %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # Inherited methods that can be used by all connectors
    
    def get_sample(self, key) :
        """
        Wrapper around the __get_item__ method if you prefer a more expicit/descriptive function name.

        Returns
        -------
        sample
            A single data sample retrieved from the data source. The format of the sample will depend on the specific implementation of the connector.
        """

        return self.__get_item__(key)

    def compare_numerical_features(self, feature : str, comparison_type : str, filter_value, return_int_idx : bool = False) :
        """
        Function that alreay implement the comparison between a feature and a filter value when the feature is expressed as a 1D array.
        Since this kind of comparison is common for a lot of data type that store tabular data (e.g. CSV files, databases, etc.), this function can be used by all the connectors that works with this kind of data.

        Note that this function use get_feature to retrieve the feautre values and convert them to a numpy array, so it requires the implementation of a get_feature method that returns values that can be converted to a numpy array.

        Parameters
        ----------
        feature : str
            The name of the feature to compare.
        comparison_type : str
            The type of comparison to perform. Supported comparison types are: 'equals', 'not_equals', 'greater_than', 'less_than', 'less_than_or_equal', 'greater_than_or_equal'.
        filter_value
            The value to compare the feature values against for filtering.
        return_int_idx : bool, optional
            Whether to return the integer indices of the samples that satisfy the specified filter condition instead of a boolean array. 
            If True, the function will return a numpy array containing the integer indices of the samples that satisfy the specified filter condition. 
            If False (default), the function will return a boolean array where each element is True if the corresponding sample satisfies the specified filter condition and False otherwise.
        """

        feature_values = np.asarray(self.get_feature(feature))

        if comparison_type == 'equals' :
            bool_idx = feature_values == filter_value
        elif comparison_type == 'not_equals' :
            bool_idx = feature_values != filter_value
        elif comparison_type == 'greater_than' :
            bool_idx = feature_values > filter_value
        elif comparison_type == 'less_than' :
            bool_idx = feature_values < filter_value
        elif comparison_type == 'less_than_or_equal' :
            bool_idx = feature_values <= filter_value
        elif comparison_type == 'greater_than_or_equal' :
            bool_idx = feature_values >= filter_value
        else :
            raise ValueError(f"Unsupported comparison type '{comparison_type}'. Supported comparison types are: {self.SUPPORTED_COMPARISON_TYPE}")

        if return_int_idx :
            return np.where(bool_idx)[0]
        else :
            return bool_idx
    
    def filter_based_on_feature_value(self, feature : str, comparison_type : str, filter_value) :
        """
        Return the samples that satisfy the specified filter condition based on a feature value.

        It required the implementation of the get_filtered_keys method, which is necessary to retrieve the keys of the samples that satisfy the specified filter condition.
        """
        
        # Get the keys of the samples that satisfy the specified filter condition based on a feature value using the get_filtered_keys method implemented by the specific connector.
        try :
            filtered_keys = self.get_filtered_keys(feature, comparison_type, filter_value)
        except NotImplementedError :
            raise NotImplementedError(f"The filter_based_on_feature_value method requires the implementation of the get_filtered_keys method, which is not supported by the data connector used in this dataset. The specific implementation of the data connector must implement the get_filtered_keys method to use this functionality.")
        
        # Check if the filtered_keys are ok
        try :
            # Check if I have at least one key that satisfy the specified filter condition, otherwise raise an error with a clear message.
            if len(filtered_keys) == 0 :
                raise ValueError(f"No samples satisfy the specified filter condition: feature '{feature}' {comparison_type} {filter_value}.")
        except TypeError :
            # If the filtered_keys is not an iterable (e.g., it is None, a single value, etc.), raise an error with a clear message.
            raise ValueError(f"The get_filtered_keys method should return an iterable of keys, but it returned a non-iterable value: {filtered_keys}. Please check the implementation of the get_filtered_keys method.")
        
        # Get the keys of the samples that satisfy the specified filter condition
        try :
            return self.__get_item__(filtered_keys)
        except Exception as e :
            original_error = str(e)
        
        # If there is an error during the retrieval of the samples using the __get_item__ method, raise an error with a clear message that includes the original error message and some additional context to help understand the issue.
        full_error_mesasge = f"Failed to retrieve the samples corresponding to the filtered keys: {filtered_keys}."
        full_error_mesasge += f"\nThe get_filtered_keys method seems to be working correctly, as it returned the filtered keys without any issues. However, there is an issue with retrieving the samples using the __get_item__ method."
        full_error_mesasge += f"\nNote that the output of the get_filtered_keys method is being passed directly as an argument to the __get_item__ method, and the error occurs during this step. The specific error message from the __get_item__ method is: {original_error}. "
        full_error_mesasge += f"\nPlease check the implementation of the __get_item__/get_filtered_keys methods"

        raise ValueError(full_error_mesasge)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_connector(connector_config : generic.connector_config) -> data_connector :
    """
    Based on the config received, return the appropriate connector.

    Parameters
    ----------
    connector_config : generic_connector_config
        The configuration object for the data connector, which includes the modality and any specific parameters needed to initialize the connector.
    """

    modality = connector_config.modality

    if modality == 'csv' :
        from clinnova_fl.data_connector.csv import data_connector
    elif modality == 'synthetic' :
        from clinnova_fl.data_connector.synthetic import data_connector
    else :
        raise ValueError(f'Modality {modality} not supported. Currently supported modalities are: {generic.SUPPORTED_COMPARISON_TYPE}')

    return data_connector(connector_config)




