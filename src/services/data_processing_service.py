"""Main data processing service."""

from pathlib import Path
from typing import Any, Dict, List

from loguru import logger

from ..interfaces.data_interfaces import IConfigService, IDataTransformer, IDatabaseService
from ..interfaces.parser_interface import IParserFactory


class DataProcessingService:
    """Main service for processing data from partners."""
    
    def __init__(
        self,
        parser_factory: IParserFactory,
        data_transformer: IDataTransformer,
        database_service: IDatabaseService,
        config_service: IConfigService
    ):
        """Initialize data processing service."""
        self.parser_factory = parser_factory
        self.data_transformer = data_transformer
        self.database_service = database_service
        self.config_service = config_service
        logger.info("Data processing service initialized")
    
    def process_partner_data(self, partner_id: str, data_sources_path: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Process data for a specific partner.
        
        Args:
            partner_id: Partner identifier
            data_sources_path: Path to data sources directory
            dry_run: If True, only validate without inserting to database
            
        Returns:
            Processing results
        """
        logger.info(f"Processing data for partner: {partner_id}")
        
        result = {
            'partner_id': partner_id,
            'success': False,
            'files_processed': 0,
            'records_processed': 0,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Load partner configuration
            config = self.config_service.load_partner_config(partner_id)
            
            # Find partner data directory
            partner_data_path = Path(data_sources_path) / partner_id
            if not partner_data_path.exists():
                # Try to find directory with case-insensitive match
                partner_data_path = self._find_partner_directory(data_sources_path, partner_id)
                if not partner_data_path:
                    raise FileNotFoundError(f"Data directory not found for partner: {partner_id}")
            
            # Get all files in partner directory
            data_files = self._get_data_files(partner_data_path)
            
            if not data_files:
                result['warnings'].append("No data files found")
                return result
            
            # Process each file
            for file_path in data_files:
                try:
                    file_result = self._process_file(file_path, config, dry_run)
                    result['files_processed'] += 1
                    result['records_processed'] += file_result['records_processed']
                    result['warnings'].extend(file_result['warnings'])
                    
                except Exception as e:
                    error_msg = f"Failed to process file {file_path}: {e}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
            
            result['success'] = len(result['errors']) == 0
            
            if result['success']:
                logger.info(f"Successfully processed {result['files_processed']} files "
                           f"with {result['records_processed']} records for partner {partner_id}")
            else:
                logger.error(f"Processing completed with errors for partner {partner_id}")
            
            return result
            
        except Exception as e:
            error_msg = f"Failed to process partner {partner_id}: {e}"
            logger.error(error_msg)
            result['errors'].append(error_msg)
            return result