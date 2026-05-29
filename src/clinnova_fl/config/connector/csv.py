"""
Configuration classes for data connectors

Authors
-------
Alberto (Jesus) Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Literal
from pathlib import Path
import toml

from clinnova_fl.config.connector.generic import generic_connector_config

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

SUPPORTED_FILTER_TYPES = {
    'equals',
    'less_than',
    'greater_than',
    'less_than_or_equal_to',
    'greater_than_or_equal_to'
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


@dataclass
class csv_connector_config(generic_connector_config):
    """
    Configuration for CSV data connector, used to extract data from CSV files, with optional filtering.
    
    Attributes
    ----------
    file_path : str or Path
        Path to the CSV file.
    field_name : str
        Name of the field to extract from the CSV file (for single array extraction).
    filter_field : Optional[str]
        Name of the field to use for filtering the data. If None, no filtering is applied.
        Default is None.
    filter_type : Optional[Literal['equals', 'less_than', 'greater_than', 'less_than_or_equal_to', 'greater_than_or_equal_to']]
        Type of filtering to apply. Used only if 'filter_field' is not None.
        Supported values: 'equals', 'less_than', 'greater_than', 'less_than_or_equal_to', 'greater_than_or_equal_to'.
        Default is None.
    filter_value : Optional[str]
        Value to filter by. Used only if 'filter_field' is not None.
        If 'filter_field' is not None keep only the rows that satisfy the condition defined by 'filter_field', 'filter_type' and 'filter_value'.
        E.g. if you have a csv file with several fields, and 'filter_field' is 'age', 'filter_type' is 'greater_than' and 'filter_value' is 30, then it will keep only the rows where the value of the 'age' field is greater than 30.
        Default is None.
        
    Examples
    --------
    Basic usage without filtering:
    
    >>> config = csv_connector_config(
    ...     file_path="data.csv",
    ...     field_name="age"
    ... )
    
    With filtering:
    
    >>> config = csv_connector_config(
    ...     file_path="data.csv",
    ...     field_name="weight",
    ...     filter_field="age",
    ...     filter_type="equals",
    ...     filter_value="30"
    ... )
    """
    
    modality : str = 'csv'
    file_path: str | Path
    field_name: str
    filter_field: Optional[str] = None
    filter_type: Optional[Literal[
        'equals',
        'less_than',
        'greater_than',
        'less_than_or_equal_to',
        'greater_than_or_equal_to'
    ]] = None
    filter_value: Optional[str] = None
    
    def __post_init__(self) -> None :
        """
        Validate the configuration after initialization.
        """

        # Validate required fields
        if self.file_path is None  : raise ValueError("file_path must be specified")
        if self.field_name is None : raise ValueError("field_name must be specified")

        # Convert file_path to Path object if it's a string
        if isinstance(self.file_path, str) : self.file_path = Path(self.file_path)
        
        # Validate filter configuration
        if self.filter_field is not None:
            # Check if filter_type is specified
            if self.filter_type is None : raise ValueError("filter_type must be specified when filter_field is provided")
            
            # Check if filter_value is specified
            if self.filter_value is None : raise ValueError("filter_value must be specified when filter_field is provided")

            # Check if filter_type is supported
            if self.filter_type not in SUPPORTED_FILTER_TYPES : raise ValueError(f"Filter type '{self.filter_type}' not supported. Supported filter types are: {', '.join(sorted(SUPPORTED_FILTER_TYPES))}")
        else:
            # If filter_field is None, set to None the other filter parameters

            if self.filter_type is not None : print("Warning: filter_type is specified but filter_field is None. Ignoring filter_type.")
            self.filter_type = None

            if self.filter_value is not None : print("Warning: filter_value is specified but filter_field is None. Ignoring filter_value.")
            self.filter_value = None
    
    def to_dict(self) -> dict:
        """
        Convert config to dictionary format.
        """

        config_dict = {
            'file_path': str(self.file_path),
            'field_name': self.field_name,
        }
        
        if self.filter_field is not None:
            config_dict['filter_field'] = self.filter_field
            config_dict['filter_type']  = self.filter_type
            config_dict['filter_value'] = self.filter_value
        else :
            config_dict['filter_field'] = None
            config_dict['filter_type']  = None
            config_dict['filter_value'] = None
        
        return config_dict
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> csv_connector_config:
        """
        Load configuration from a dictionary.
        
        Parameters
        ----------
        config_dict : dict
            Dictionary containing the configuration data with keys:
            'file_path', 'field_name', and optional 'filter_field', 'filter_type', 'filter_value'.
        
        Returns
        -------
        csv_connector_config
            A new instance of csv_connector_config loaded from the dictionary.
        
        Raises
        ------
        ValueError
            If the dictionary has invalid or missing required values.
        
        Examples
        --------
        >>> config_dict = {'file_path': 'data.csv', 'field_name': 'age'}
        >>> config = csv_connector_config.from_dict(config_dict)
        """
        
        # Extract fields with defaults
        file_path    = config_dict.get('file_path')
        field_name   = config_dict.get('field_name')
        filter_field = config_dict.get('filter_field', None)
        filter_type  = config_dict.get('filter_type' , None)
        filter_value = config_dict.get('filter_value', None)
        
        # Create and return instance (validation will be done in __post_init__)
        return cls(
            file_path    = file_path,
            field_name   = field_name,
            filter_field = filter_field,
            filter_type  = filter_type,
            filter_value = filter_value
        )
