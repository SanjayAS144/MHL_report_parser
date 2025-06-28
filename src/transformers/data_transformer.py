"""Data transformation implementation."""

from datetime import datetime
from typing import Any, Dict

import pandas as pd
from loguru import logger

from ..interfaces.data_interfaces import IDataTransformer


class DataTransformer(IDataTransformer):
    """Implementation of data transformer."""
    
    def transform(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """
        Transform data according to configuration.
        
        Args:
            df: Input DataFrame
            config: Transformation configuration
            
        Returns:
            Transformed DataFrame
        """
        logger.debug(f"Transforming DataFrame with {len(df)} rows")
        
        try:
            # Create a copy to avoid modifying original
            transformed_df = df.copy()
            
            # Apply column mappings
            column_mappings = config.get('column_mappings', [])
            transformed_df = self._apply_column_mappings(transformed_df, column_mappings)
            
            # Apply global transformations
            global_transformations = config.get('global_transformations', [])
            transformed_df = self._apply_global_transformations(transformed_df, global_transformations)
            
            # Apply filters
            filters = config.get('filters', {})
            transformed_df = self._apply_filters(transformed_df, filters)
            
            logger.debug(f"Transformation complete. Result: {len(transformed_df)} rows")
            return transformed_df
            
        except Exception as e:
            logger.error(f"Transformation failed: {e}")
            raise
    
    def _apply_column_mappings(self, df: pd.DataFrame, column_mappings: list) -> pd.DataFrame:
        """Apply column mappings and transformations."""
        result_df = pd.DataFrame()
        
        for mapping in column_mappings:
            source_column = mapping['source_column']
            system_column = mapping['system_column']
            column_type = mapping['column_type']
            default_value = mapping.get('default_value')
            transformations = mapping.get('transformations', [])
            required = mapping.get('required', True)
            
            logger.debug(f"Mapping {source_column} -> {system_column}")
            
            # Check if source column exists
            if source_column not in df.columns:
                if required:
                    if default_value is not None:
                        result_df[system_column] = default_value
                        logger.warning(f"Required column '{source_column}' not found, using default value")
                    else:
                        logger.error(f"Required column '{source_column}' not found and no default provided")
                        raise ValueError(f"Required column '{source_column}' not found")
                else:
                    logger.debug(f"Optional column '{source_column}' not found, skipping")
                    continue
            else:
                # Copy the column
                result_df[system_column] = df[source_column].copy()
                
                # Apply column-specific transformations
                result_df[system_column] = self._apply_column_transformations(
                    result_df[system_column], transformations
                )
                
                # Apply data type conversion
                result_df[system_column] = self._convert_data_type(
                    result_df[system_column], column_type, default_value
                )
        
        return result_df
    
    def _apply_column_transformations(self, series: pd.Series, transformations: list) -> pd.Series:
        """Apply transformations to a specific column."""
        result = series.copy()
        
        for transform in transformations:
            transform_type = transform.get('type')
            
            if transform_type == 'uppercase':
                result = result.astype(str).str.upper()
            elif transform_type == 'lowercase':
                result = result.astype(str).str.lower()
            elif transform_type == 'strip':
                result = result.astype(str).str.strip()
            elif transform_type == 'replace':
                old_value = transform.get('old_value', '')
                new_value = transform.get('new_value', '')
                result = result.astype(str).str.replace(old_value, new_value)
            elif transform_type == 'date_format':
                input_format = transform.get('input_format')
                result = self._parse_dates(result, input_format)
            elif transform_type == 'numeric_conversion':
                result = pd.to_numeric(result, errors='coerce')
            elif transform_type == 'split':
                delimiter = transform.get('delimiter', ',')
                index = transform.get('index', 0)
                result = result.astype(str).str.split(delimiter).str[index]
            elif transform_type == 'concat':
                suffix = transform.get('suffix', '')
                prefix = transform.get('prefix', '')
                result = prefix + result.astype(str) + suffix
            else:
                logger.warning(f"Unknown transformation type: {transform_type}")
        
        return result
    
    def _convert_data_type(self, series: pd.Series, column_type: str, default_value: Any) -> pd.Series:
        """Convert series to specified data type."""
        try:
            if column_type == 'string':
                return series.astype(str)
            elif column_type == 'integer':
                return pd.to_numeric(series, errors='coerce').fillna(default_value or 0).astype(int)
            elif column_type == 'float':
                return pd.to_numeric(series, errors='coerce').fillna(default_value or 0.0)
            elif column_type == 'decimal':
                return pd.to_numeric(series, errors='coerce').fillna(default_value or 0.0)
            elif column_type == 'boolean':
                return series.astype(bool)
            elif column_type in ['date', 'datetime']:
                return self._parse_dates(series)
            else:
                logger.warning(f"Unknown column type: {column_type}, treating as string")
                return series.astype(str)
        except Exception as e:
            logger.warning(f"Failed to convert column to {column_type}: {e}, treating as string")
            return series.astype(str)
    
    def _parse_dates(self, series: pd.Series, date_format: str = None) -> pd.Series:
        """Parse dates with optional format."""
        try:
            if date_format:
                return pd.to_datetime(series, format=date_format, errors='coerce')
            else:
                return pd.to_datetime(series, errors='coerce', infer_datetime_format=True)
        except Exception as e:
            logger.warning(f"Failed to parse dates: {e}")
            return series
    
    def _apply_global_transformations(self, df: pd.DataFrame, transformations: list) -> pd.DataFrame:
        """Apply global transformations to the entire DataFrame."""
        result_df = df.copy()
        
        for transform in transformations:
            transform_type = transform.get('type')
            
            if transform_type == 'remove_empty_rows':
                result_df = result_df.dropna(how='all')
            elif transform_type == 'remove_duplicates':
                result_df = result_df.drop_duplicates()
            elif transform_type == 'sort':
                columns = transform.get('columns', [])
                ascending = transform.get('ascending', True)
                if columns:
                    result_df = result_df.sort_values(by=columns, ascending=ascending)
            else:
                logger.warning(f"Unknown global transformation type: {transform_type}")
        
        return result_df
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the DataFrame."""
        if not filters:
            return df
        
        result_df = df.copy()
        
        for column, filter_config in filters.items():
            if column not in result_df.columns:
                logger.warning(f"Filter column '{column}' not found")
                continue
            
            filter_type = filter_config.get('type', 'equals')
            filter_value = filter_config.get('value')
            
            if filter_type == 'equals':
                result_df = result_df[result_df[column] == filter_value]
            elif filter_type == 'not_equals':
                result_df = result_df[result_df[column] != filter_value]
            elif filter_type == 'contains':
                result_df = result_df[result_df[column].astype(str).str.contains(str(filter_value), na=False)]
            elif filter_type == 'not_null':
                result_df = result_df[result_df[column].notna()]
            elif filter_type == 'is_null':
                result_df = result_df[result_df[column].isna()]
            else:
                logger.warning(f"Unknown filter type: {filter_type}")
        
        return result_df 