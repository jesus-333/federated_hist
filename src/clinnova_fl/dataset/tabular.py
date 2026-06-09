"""
Tabular dataset implementation. 

Note that this dataset use the tidy data format, where each sample is represented as a row of a table, and the columns represent the features of the samples.
See https://data.europa.eu/apps/data-visualisation-guide/intro-to-tidy-data for more details on the tidy data format.

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

# General imports
import numpy as np
import torch

# Internal imports
from clinnova_fl.data_connector.generic import data_connector
from clinnova_fl.dataset.generic import dataset

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


class dataset(dataset):
    """
    Tabular dataset implementation.

    Attributes
    ----------
    dataset_id : str
        The unique identifier of the dataset.
    data_connector : data_connector
        The data connector used to retrieve the data for this dataset.
    return_type : str
        The type of the returned sample (e.g., 'numpy', 'torch', etc.).
    """

    def __init__(self, dataset_id : str, data_connector : data_connector, return_type : str = 'numpy') :
        """
        """

        self.SUPPORTED_RETURN_TYPES = ['numpy', 'torch']

        self.dataset_id = dataset_id
        self.data_connector = data_connector

        if return_type not in self.SUPPORTED_RETURN_TYPES :
            raise ValueError(f"Unsupported return type '{return_type}'. Supported return types are: {self.SUPPORTED_RETURN_TYPES}")
        self.return_type = return_type
    
    def __get_item__(self, row_idx) :
        """
        Return the row(s) specified by row_idx. 

        Parameters
        ----------
        row_idx : int or list of int
            The index or indices of the row(s) to retrieve. The specific format of row_idx depends on the implementation of the data connector and the dataset. For example, it could be a single integer index, a list of integer indices, a slice object, etc.

        Returns
        -------
        sample(s)
                The row(s) specified by row_idx. The specific format of the returned sample(s) depends on the return_type specified during the initialization of the dataset.
                If return_type is 'numpy', the returned sample(s) will be in the form of a numpy array, if return_type is 'torch', the returned sample(s) will be in the form of a torch tensor, etc.
                To see the supported return types for this dataset, you can use the show_supported_return_types() method.
        """

        sample = self.data_connector[row_idx]

        if self.return_type == 'numpy' :
            return np.array(sample)
        elif self.return_type == 'torch' :
            return torch.tensor(sample)

    def get_feature(self, feature_name : str) :
        """
        Get a specific feature from the dataset.

        Parameters
        ----------
        feature_name : str
            The name of the feature to retrieve.

        Returns
        -------
        feature_values
                The values of the specified feature for all samples in the dataset. The specific format of the returned feature values depends on the return_type specified during the initialization of the dataset.
                If return_type is 'numpy', the returned feature values will be in the form of a numpy array, if return_type is 'torch', the returned feature values will be in the form of a torch tensor, etc.
                To see the supported return types for this dataset, you can use the show_supported_return_types() method.
        """
        
        try :
            feature_values = self.data_connector.get_feature(feature_name)
        except NotImplementedError :
            raise NotImplementedError(f"The get_feature method is not supported by the data connector used in this dataset. The specific implementation of the data connector must implement the get_feature method to use this functionality.")
        except Exception as e :
            raise e

        if self.return_type == 'numpy' :
            return np.array(feature_values)
        elif self.return_type == 'torch' :
            return torch.tensor(feature_values)
    
    # TODO : Move to generic daataset? 
    def show_supported_return_types(self) :
        """
        Print the supported return types for this dataset.
        """
        
        # Separate each supported return type (declared here as variable because is quicker to update)
        separator = "\n- "
        
        # Create nice string with the supported return types.
        supported_return_types_nice_format = separator + separator.join(self.SUPPORTED_RETURN_TYPES)
        # Small notes... the join method add the specified string (in this case, "\n- ") between each element of the list (in this case, self.SUPPORTED_RETURN_TYPES).
        # So, if I do not put the "\n- " at the beginning, the first element of the list will not have it.

        print(f"Supported return types for this dataset are :\n{supported_return_types_nice_format}")
    
