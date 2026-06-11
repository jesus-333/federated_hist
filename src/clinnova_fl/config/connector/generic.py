"""
Generic connector configuration base class

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
import toml

# Note
# ABC stands for Abstract Base Class, and it is used to define abstract classes that cannot be instantiated directly, but can be subclassed.
# The abstract methods defined in the ABC must be implemented by any concrete subclass.
# abstractmethod provide a decorator to indicate methods that must be implemented by subclasses. If a subclass does not implement all abstract methods, it cannot be instantiated.


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

SUPPORTED_MODALITY = [
    'csv'
    'synthetic',
]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

@dataclass
class connector_config(ABC):
    """
    Abstract base class for all connector configurations.
    
    This class provides a template for creating specific connector configurations (e.g., CSV, JSON, database connectors). All connector config classes should inherit from this class and implement the required abstract methods.
    
    Methods
    -------
    to_dict()
        Convert the configuration to a dictionary format.
    from_dict(config_dict)
        Load configuration from a dictionary.
    from_toml(toml_path)
        Load configuration from a TOML file.
    
    Examples
    --------
    Creating a custom connector by inheriting from connector_config:
    
    >>> @dataclass
    ... class my_connector_config(connector_config):
    ...     file_path: str
    ...     
    ...     def __post_init__(self):
    ...         self.validate()
    ...     
    ...     def to_dict(self) -> dict:
    ...         return {'file_path': str(self.file_path)}
    ...     
    ...     @classmethod
    ...     def from_dict(cls, config_dict: dict):
    ...         # Load from dict and return instance
    ...         return cls(**config_dict)
    ...     
    ...     def from_toml(cls, toml_path: str | Path):
    ...         # Load from TOML and return instance
    ...         pass
    """

    # Class attribute: must be overridden in each child class
    modality: str = None

    def __post_init__(self) -> None:
        """
        Validate the configuration after initialization.
        
        This method should be overridden by subclasses to perform specific validation logic.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary format.
        
        This method must be implemented by all subclasses to provide a dictionary representation of the configuration that can be used by connector functions.
        
        Returns
        -------
        dict
            Dictionary representation of the configuration.
        """
        raise NotImplementedError("Subclasses must implement to_dict()")

    @classmethod
    @abstractmethod
    def from_dict(cls, config_dict: dict) -> connector_config:
        """
        Load configuration from a dictionary.
        
        This method must be implemented by all subclasses to load configuration from a dictionary and return a properly initialized instance.
        
        Parameters
        ----------
        config_dict : dict
            Dictionary containing the configuration data.
        
        Returns
        -------
        connector_config
            A new instance loaded from the dictionary.
        
        Raises
        ------
        ValueError
            If the dictionary has invalid or missing values.
            
        Examples
        --------
        >>> config_dict = {'file_path': 'data.csv', 'field_name': 'age'}
        >>> config = csv_connector_config.from_dict(config_dict)
        """
        raise NotImplementedError("Subclasses must implement from_dict()")

    @classmethod
    def from_toml(cls, toml_path: str | Path) -> connector_config :
        """
        Load configuration from a TOML file.
        
        This method is shared by all subclasses to load configuration from a TOML file and return a properly initialized instance. 
        It uses the from_dict method to create the instance after loading the TOML file.
        
        Parameters
        ----------
        toml_path : str or Path
            Path to the TOML configuration file.
        
        Returns
        -------
        connector_config
            A new instance loaded from the TOML file.
        
        Raises
        ------
        FileNotFoundError
            If the TOML file does not exist.
        ValueError
            If the TOML file cannot be parsed or has invalid values.
            
        Examples
        --------
        >>> config = csv_connector_config.from_toml("csv_config.toml")
        """

        # Convert to Path object if necessary
        toml_path = Path(toml_path) if isinstance(toml_path, str) else toml_path
        
        # Check if file exists
        if not toml_path.exists() : raise FileNotFoundError(f"TOML configuration file not found: {toml_path}")
        
        # Load TOML file
        try:
            config_data = toml.load(str(toml_path))
        except Exception as e :
            raise ValueError(f"Failed to parse TOML file '{toml_path}': {e}")
        
        # Use from_dict to create the instance
        return cls.from_dict(config_data)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def get_connector_config(connector_config_dict : dict) :
    """
    Based on the config dictionary received, return the appropriate connector config.
    """

    modality = connector_config_dict['modality']

    if modality == 'csv' :
        from clinnova_fl.config.connector.csv import csv_connector_config
        connector_config = csv_connector_config.from_dict(connector_config_dict)
    elif modality == 'synthetic' :
        from clinnova_fl.config.connector.synthetic import synthetic_connector_config
        connector_config = synthetic_connector_config.from_dict(connector_config_dict)
    else :
        raise ValueError(f'Modality {modality} not supported. Currently supported modalities are: {SUPPORTED_MODALITY}')

    return connector_config
