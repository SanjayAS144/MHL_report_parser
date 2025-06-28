"""Pydantic models for configuration validation."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class FileFormat(str, Enum):
    """Supported file formats."""
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class ColumnType(str, Enum):
    """Supported column data types."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"
    DATE = "date"
    DATETIME = "datetime"
    BOOLEAN = "boolean"


class TransformationType(str, Enum):
    """Supported transformation types."""
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"
    STRIP = "strip"
    REPLACE = "replace"
    DATE_FORMAT = "date_format"
    NUMERIC_CONVERSION = "numeric_conversion"
    SPLIT = "split"
    CONCAT = "concat"


    class ColumnMapping(BaseModel):
    """Configuration for column mapping."""
    source_column: str = Field(..., description="Source column name")
    system_column: str = Field(..., description="Target system column name")
    column_type: ColumnType = Field(..., description="Data type of the column")
    required: bool = Field(default=True, description="Whether column is required")
    default_value: Optional[Any] = Field(default=None, description="Default value if missing")
    transformations: List[Dict[str, Any]] = Field(default_factory=list, description="List of transformations")


class SheetConfig(BaseModel):
    """Configuration for individual sheet/table."""
    sheet_name: str = Field(..., description="Sheet name or CSV filename")
    target_table: str = Field(..., description="Target database table")
    headers_row: int = Field(default=1, description="Row number containing headers")
    data_start_row: Optional[int] = Field(default=None, description="Row where data starts (defaults to headers_row + 1)")
    skip_rows: List[int] = Field(default_factory=list, description="Row numbers to skip")
    column_mappings: List[ColumnMapping] = Field(..., description="Column mapping configurations")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Row filters to apply")

    @validator('data_start_row', always=True)
    def set_data_start_row(cls, v, values):
        if v is None and 'headers_row' in values:
            return values['headers_row'] + 1
        return v


class SourceConfig(BaseModel):
    """Configuration for data source."""
    file_format: FileFormat = Field(..., description="File format")
    encoding: str = Field(default="utf-8", description="File encoding")
    sheets_config: List[SheetConfig] = Field(..., description="Sheet configurations")
    global_transformations: List[Dict[str, Any]] = Field(default_factory=list, description="Global transformations")


class PartnerConfig(BaseModel):
    """Complete partner configuration."""
    partner_id: str = Field(..., description="Unique partner identifier")
    partner_name: str = Field(..., description="Partner display name")
    template_id: str = Field(..., description="Template identifier")
    description: Optional[str] = Field(default=None, description="Configuration description")
    version: str = Field(default="1.0", description="Configuration version")
    source_config: SourceConfig = Field(..., description="Source data configuration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('partner_id')
    def validate_partner_id(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('partner_id must contain only alphanumeric characters, hyphens, and underscores')
        return v.lower()


class AppConfig(BaseModel):
    """Application configuration."""
    db_host: str = Field(..., description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(..., description="Database name")
    db_user: str = Field(..., description="Database user")
    db_password: str = Field(..., description="Database password")
    db_schema: str = Field(default="public", description="Database schema")
    
    log_level: str = Field(default="INFO", description="Logging level")
    log_file_path: str = Field(default="logs/data_parser.log", description="Log file path")
    
    data_sources_path: str = Field(default="../Data_Sources", description="Data sources directory")
    configs_path: str = Field(default="configs/partners", description="Configurations directory")
    
    batch_size: int = Field(default=1000, description="Database batch size")
    max_workers: int = Field(default=4, description="Maximum worker threads")
    enable_validation: bool = Field(default=True, description="Enable data validation")
    
    debug: bool = Field(default=False, description="Debug mode")
    dry_run: bool = Field(default=False, description="Dry run mode")

    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v.upper() 