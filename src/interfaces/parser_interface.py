"""Abstract interface for file parsers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class IFileParser(ABC):
    """Abstract interface for file parsers."""

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        pass

    @abstractmethod
    def parse(self, file_path: Path, config: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """
        Parse file and return dataframes.
        
        Args:
            file_path: Path to the file to parse
            config: Configuration for parsing
            
        Returns:
            Dictionary mapping sheet/table names to DataFrames
        """
        pass

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        pass


class IParserFactory(ABC):
    """Abstract interface for parser factory."""

    @abstractmethod
    def get_parser(self, file_path: Path) -> Optional[IFileParser]:
        """Get appropriate parser for the given file."""
        pass

    @abstractmethod
    def register_parser(self, parser: IFileParser) -> None:
        """Register a new parser."""
        pass 