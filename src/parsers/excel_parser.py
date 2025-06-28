"""Excel file parser implementation."""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from loguru import logger

from ..interfaces.parser_interface import IFileParser


class ExcelParser(IFileParser):
    """Parser for Excel files (.xlsx, .xls)."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.suffix.lower() in ['.xlsx', '.xls']
    
    def parse(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Parse Excel file and return dataframes.
        
        Args:
            file_path: Path to the Excel file
            config: Configuration containing sheet information
            
        Returns:
            Dictionary mapping sheet names to DataFrames
        """
        logger.info(f"Parsing Excel file: {file_path}")
        
        try:
            sheets_config = config.get('sheets_config', [])
            result = {}
            
            for sheet_config in sheets_config:
                sheet_name = sheet_config['sheet_name']
                headers_row = sheet_config.get('headers_row', 1) - 1  # Convert to 0-based
                data_start_row = sheet_config.get('data_start_row', headers_row + 1) - 1
                skip_rows = sheet_config.get('skip_rows', [])
                
                logger.debug(f"Reading sheet: {sheet_name}")
                
                try:
                    # Read the sheet
                    df = pd.read_excel(
                        file_path,
                        sheet_name=sheet_name,
                        header=headers_row,
                        skiprows=skip_rows,
                        engine='openpyxl' if file_path.suffix == '.xlsx' else 'xlrd'
                    )
                    
                    # Skip additional rows if needed
                    if data_start_row > headers_row:
                        rows_to_skip = data_start_row - headers_row - 1
                        df = df.iloc[rows_to_skip:]
                    
                    # Clean column names
                    df.columns = df.columns.astype(str).str.strip()
                    
                    # Remove completely empty rows
                    df = df.dropna(how='all')
                    
                    # Reset index
                    df = df.reset_index(drop=True)
                    
                    result[sheet_name] = df
                    logger.debug(f"Successfully parsed sheet '{sheet_name}' with {len(df)} rows")
                    
                except Exception as e:
                    logger.error(f"Failed to parse sheet '{sheet_name}': {e}")
                    # Continue with other sheets
                    continue
            
            logger.info(f"Successfully parsed {len(result)} sheets from {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse Excel file {file_path}: {e}")
            raise
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.xlsx', '.xls']
    
    def get_sheet_names(self, file_path: Path) -> List[str]:
        """Get list of sheet names in the Excel file."""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            logger.error(f"Failed to get sheet names from {file_path}: {e}")
            return [] 