"""Configuration service implementation."""

import json
from pathlib import Path
from typing import Any, Dict, List

from loguru import logger
from pydantic import ValidationError

from ..config.models import PartnerConfig
from ..interfaces.data_interfaces import IConfigService


class ConfigService(IConfigService):
    """Service for managing partner configurations."""
    
    def __init__(self, configs_path: str = "configs/partners"):
        """Initialize configuration service."""
        self.configs_path = Path(configs_path)
        self.configs_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Configuration service initialized with path: {self.configs_path}")
    
    def load_partner_config(self, partner_id: str) -> Dict[str, Any]:
        """
        Load configuration for a specific partner.
        
        Args:
            partner_id: Partner identifier
            
        Returns:
            Partner configuration dictionary
        """
        config_file = self.configs_path / f"{partner_id}.json"
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Validate configuration
            validated_config = PartnerConfig(**config_data)
            
            logger.info(f"Loaded configuration for partner: {partner_id}")
            return validated_config.dict()
            
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Failed to load configuration for {partner_id}: {e}")
            raise
    
    def get_all_partner_configs(self) -> List[Dict[str, Any]]:
        """
        Get configurations for all partners.
        
        Returns:
            List of partner configurations
        """
        configs = []
        
        for config_file in self.configs_path.glob("*.json"):
            try:
                partner_id = config_file.stem
                config = self.load_partner_config(partner_id)
                configs.append(config)
            except Exception as e:
                logger.error(f"Failed to load config from {config_file}: {e}")
                continue
        
        logger.info(f"Loaded {len(configs)} partner configurations")
        return configs
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate partner configuration.
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            Validation results with errors and warnings
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Validate using Pydantic model
            validated_config = PartnerConfig(**config)
            
            # Additional business logic validations
            self._validate_business_rules(validated_config, result)
            
            logger.debug(f"Configuration validation completed for {config.get('partner_id', 'unknown')}")
            
        except ValidationError as e:
            result['valid'] = False
            for error in e.errors():
                result['errors'].append({
                    'field': '.'.join(str(x) for x in error['loc']),
                    'message': error['msg'],
                    'type': error['type']
                })
            logger.error(f"Configuration validation failed: {e}")
        
        return result
    
    def save_partner_config(self, config: Dict[str, Any]) -> bool:
        """
        Save partner configuration to file.
        
        Args:
            config: Configuration dictionary to save
            
        Returns:
            Success status
        """
        try:
            # Validate first
            validation_result = self.validate_config(config)
            if not validation_result['valid']:
                logger.error(f"Cannot save invalid configuration: {validation_result['errors']}")
                return False
            
            partner_id = config['partner_id']
            config_file = self.configs_path / f"{partner_id}.json"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved configuration for partner: {partner_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def list_partners(self) -> List[str]:
        """Get list of available partner IDs."""
        partners = []
        for config_file in self.configs_path.glob("*.json"):
            partners.append(config_file.stem)
        return sorted(partners)
    
    def _validate_business_rules(self, config: PartnerConfig, result: Dict[str, Any]):
        """Validate business-specific rules."""
        # Check for duplicate system columns within a sheet
        for sheet_config in config.source_config.sheets_config:
            system_columns = []
            for mapping in sheet_config.column_mappings:
                if mapping.system_column in system_columns:
                    result['warnings'].append(f"Duplicate system column '{mapping.system_column}' in sheet '{sheet_config.sheet_name}'")
                system_columns.append(mapping.system_column)
        
        # Check if required fields are mapped
        required_fields = ['order_id', 'order_date', 'outlet_id']  # Example required fields
        for sheet_config in config.source_config.sheets_config:
            if sheet_config.target_table == 'orders':
                mapped_columns = [mapping.system_column for mapping in sheet_config.column_mappings]
                for field in required_fields:
                    if field not in mapped_columns:
                        result['warnings'].append(f"Required field '{field}' not mapped in orders table")
        
        # Validate date formats in transformations
        for sheet_config in config.source_config.sheets_config:
            for mapping in sheet_config.column_mappings:
                if mapping.column_type in ['date', 'datetime']:
                    date_format_transforms = [
                        t for t in mapping.transformations 
                        if t.get('type') == 'date_format'
                    ]
                    if not date_format_transforms:
                        result['warnings'].append(
                            f"Date/datetime column '{mapping.system_column}' has no date_format transformation"
                        ) 