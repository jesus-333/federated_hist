"""
Debug connector configuration

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from clinnova_fl.config.connector.generic import connector_config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@dataclass
class debug_connector_config(connector_config):
    """
    Configuration for debug data connector that generates synthetic data.
    
    Attributes
    ----------
    modality : str
        Always set to 'debug'.
    distribution : Literal['normal', 'uniform']
        Type of distribution for synthetic data. Default is 'normal'.
    size : int
        Number of samples to generate. Default is 100.
    seed : int
        Random seed for reproducibility. Default is 42.
    
    Examples
    --------
    >>> config = debug_connector_config(distribution='normal', size=300, seed=123)
    """
    
    modality: str = 'debug'
    seed: int = 42
    distribution: Literal['normal', 'uniform'] = 'normal'
    size_1D_array : int = 100
    
    def to_dict(self) -> dict:
        """
        Convert config to dictionary format.
        """

        config = dict(
            modality = self.modality,
            distribution = self.distribution,
            size = self.size_1D_array,
            seed = self.seed
        )

        return config
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> debug_connector_config:
        """
        Load configuration from a dictionary.
        """

        return cls(
            modality      = config_dict.get('modality', 'debug'),
            distribution  = config_dict.get('distribution', 'normal'),
            size_1D_array = config_dict.get('size', 100),
            seed          = config_dict.get('seed', 42)
        )
