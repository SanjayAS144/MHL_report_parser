"""Interfaces for data transformation and validation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd


class IDataTransformer(ABC):
    """Abstract interface for data transformers."""

    @abstractmethod
    def transform(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform data according to configuration.
        
        Args:
            df: Input DataFrame
            config: Transformation configuration
            
        Returns:
            Transformed DataFrame
        """
        pass


class IDataValidator(ABC):
    """Abstract interface for data validators."""

    @abstractmethod
    def validate(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """
        Validate data and return validation results.
        
        Args:
            df: DataFrame to validate
            table_name: Target table name
            
        Returns:
            Validation results with errors and warnings
        """
        pass


class IDatabaseService(ABC):
    """Abstract interface for database operations."""

    @abstractmethod
    def insert_data(self, df: pd.DataFrame, table_name: str, batch_size: int = 1000) -> bool:
        """
        Insert data into database table.
        
        Args:
            df: DataFrame to insert
            table_name: Target table name
            batch_size: Batch size for insertion
            
        Returns:
            Success status
        """
        pass

    @abstractmethod
    def get_existing_records(self, table_name: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Get existing records from table with filters.
        
        Args:
            table_name: Table to query
            filters: Filter conditions
            
        Returns:
            DataFrame with existing records
        """
        pass

    @abstractmethod
    def create_tables(self) -> bool:
        """Create all required tables in database."""
        pass


class IConfigService(ABC):
    """Abstract interface for configuration management."""

    @abstractmethod
    def load_partner_config(self, partner_id: str) -> Dict[str, Any]:
        """Load configuration for a specific partner."""
        pass

    @abstractmethod
    def get_all_partner_configs(self) -> List[Dict[str, Any]]:
        """Get configurations for all partners."""
        pass

    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate partner configuration."""
        pass 