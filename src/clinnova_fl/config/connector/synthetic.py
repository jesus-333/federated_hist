"""
Synthetic connector configuration, used to generate synthetic data.

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
class synthetic_connector_config(connector_config):
    """
    Configuration for synthetic data connector that generates synthetic data.
    
    Attributes
    ----------
    modality : str
        Always set to 'synthetic'.
    distribution : Literal['normal', 'uniform']
        Type of distribution for synthetic data. Default is 'normal'.
    size : int
        Number of samples to generate. Default is 100.
    seed : int
        Random seed for reproducibility. Default is 42.
    
    Examples
    --------
    >>> config = synthetic_connector_config(distribution='normal', size=300, seed=123)
    """
    
    # General parameters
    modality: str = 'synthetic'
    seed : int = 42
    distribution: Literal['normal', 'uniform'] = 'normal'
    size_1D_array : int = 100

    # Parameters for normal distribution
    loc: float = 0
    scale: float = 1

    # Parameters for uniform distribution
    low: float = 0
    high: float = 1
    
    def to_dict(self) -> dict:
        """
        Convert config to dictionary format.
        """

        config = dict(
            modality = self.modality,
            distribution = self.distribution,
            size = self.size_1D_array,
            seed = self.seed,
            # Parameters for normal distribution
            loc = self.loc if self.distribution == 'normal' else None,
            scale = self.scale if self.distribution == 'normal' else None,
            # Parameters for uniform distribution
            low = self.low if self.distribution == 'uniform' else None,
            high = self.high if self.distribution == 'uniform' else None,
        )

        return config
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> synthetic_connector_config:
        """
        Load configuration from a dictionary.
        """

        return cls(
            modality      = config_dict.get('modality', 'synthetic'),
            distribution  = config_dict.get('distribution', 'normal'),
            size_1D_array = config_dict.get('size', 100),
            seed          = config_dict.get('seed', 42),
            # Parameters for normal distribution
            loc           = config_dict.get('loc', 0),
            scale         = config_dict.get('scale', 1),
            # Parameters for uniform distribution
            low           = config_dict.get('low', 0),
            high          = config_dict.get('high', 1),
        )
