"""CSV file parser implementation."""

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from loguru import logger

from ..interfaces.parser_interface import IFileParser


class CSVParser(IFileParser):
    """Parser for CSV files."""
    
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.suffix.lower() == '.csv'
    
    def parse(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Parse CSV file and return dataframes.
        
        Args:
            file_path: Path to the CSV file
            config: Configuration containing parsing information
            
        Returns:
            Dictionary mapping file name to DataFrame
        """
        logger.info(f"Parsing CSV file: {file_path}")
        
        try:
            # Get configuration
            encoding = config.get('encoding', 'utf-8')
            sheets_config = config.get('sheets_config', [])
            
            # Find matching sheet config
            sheet_config = None
            file_name = file_path.name
            
            for sc in sheets_config:
                if sc['sheet_name'] == file_name or sc['sheet_name'] == file_path.stem:
                    sheet_config = sc
                    break
            
            if not sheet_config:
                # Use default configuration
                sheet_config = {
                    'sheet_name': file_name,
                    'headers_row': 1,
                    'skip_rows': []
                }
            
            headers_row = sheet_config.get('headers_row', 1) - 1  # Convert to 0-based
            skip_rows = sheet_config.get('skip_rows', [])
            
            logger.debug(f"Reading CSV with encoding: {encoding}")
            
            # Try to detect delimiter
            delimiter = self._detect_delimiter(file_path, encoding)
            
            # Read CSV file
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                delimiter=delimiter,
                header=headers_row,
                skiprows=skip_rows,
                low_memory=False
            )
            
            # Clean column names
            df.columns = df.columns.astype(str).str.strip()
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Reset index
            df = df.reset_index(drop=True)
            
            result = {file_path.stem: df}
            logger.info(f"Successfully parsed CSV file with {len(df)} rows")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse CSV file {file_path}: {e}")
            raise
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.csv']
    
    def _detect_delimiter(self, file_path: Path, encoding: str) -> str:
        """Detect CSV delimiter by reading first few lines."""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline()
                
            # Common delimiters to check
            delimiters = [',', ';', '\t', '|']
            delimiter_counts = {}
            
            for delim in delimiters:
                delimiter_counts[delim] = first_line.count(delim)
            
            # Return delimiter with highest count
            detected_delimiter = max(delimiter_counts, key=delimiter_counts.get)
            
            if delimiter_counts[detected_delimiter] > 0:
                logger.debug(f"Detected delimiter: '{detected_delimiter}'")
                return detected_delimiter
            else:
                logger.debug("No delimiter detected, using default comma")
                return ','
                
        except Exception as e:
            logger.warning(f"Failed to detect delimiter: {e}, using default comma")
            return ',' 