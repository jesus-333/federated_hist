"""
Image dataset implementation

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
    Image dataset implementation.

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
        
        raise NotImplemented("DATASET NOT YET IMPLEMENTED")
