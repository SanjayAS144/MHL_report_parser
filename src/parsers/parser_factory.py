"""Parser factory implementation."""

from pathlib import Path
from typing import List, Optional, Dict, Any

from loguru import logger

from ..interfaces.parser_interface import IFileParser, IParserFactory
from .csv_parser import CSVParser
from .excel_parser import ExcelParser


class ParserFactory(IParserFactory):
    """Factory for creating appropriate file parsers."""


    def __init__(self, file_path: Path, config: Dict[str, Any]):
        """Initialize parser factory with default parsers."""
        self._parsers: List[IFileParser] = []
        self._register_default_parsers()
        super().__init__(file_path, config)
    
    def _register_default_parsers(self):
        """Register default parsers."""
        self.register_parser(ExcelParser())
        self.register_parser(CSVParser())
        logger.info("Default parsers registered")
    
    def get_parser(self, file_path: Path) -> Optional[IFileParser]:
        """
        Get appropriate parser for the given file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser instance or None if no suitable parser found
        """
        for parser in self._parsers:
            if parser.can_parse(file_path):
                logger.debug(f"Found parser {parser.__class__.__name__} for file {file_path}")
                return parser
        
        logger.warning(f"No parser found for file: {file_path}")
        return None
    
    def register_parser(self, parser: IFileParser) -> None:
        """
        Register a new parser.
        
        Args:
            parser: Parser instance to register
        """
        self._parsers.append(parser)
        logger.debug(f"Registered parser: {parser.__class__.__name__}")
    
    def get_supported_extensions(self) -> List[str]:
        """Get all supported file extensions."""
        extensions = []
        for parser in self._parsers:
            extensions.extend(parser.get_supported_extensions())
        return list(set(extensions))  # Remove duplicates
    
    def list_parsers(self) -> List[str]:
        """Get list of registered parser names."""
        return [parser.__class__.__name__ for parser in self._parsers] 