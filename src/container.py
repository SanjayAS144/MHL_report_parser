"""Dependency injection container."""

import os
from dependency_injector import containers, providers

from .config.models import AppConfig
from .interfaces.data_interfaces import IConfigService, IDataTransformer, IDatabaseService
from .interfaces.parser_interface import IParserFactory
from .parsers.parser_factory import ParserFactory
from .services.config_service import ConfigService
from .services.database_service import DatabaseService
from .services.data_processing_service import DataProcessingService
from .transformers.data_transformer import DataTransformer


class ApplicationContainer(containers.DeclarativeContainer):
    """Application dependency injection container."""
    
    # Configuration
    config = providers.Configuration()
    
    # Application configuration
    app_config = providers.Singleton(
        AppConfig,
        db_host=config.db_host,
        db_port=config.db_port,
        db_name=config.db_name,
        db_user=config.db_user,
        db_password=config.db_password,
        db_schema=config.db_schema.provided.as_(str, default="public"),
        log_level=config.log_level.provided.as_(str, default="INFO"),
        log_file_path=config.log_file_path.provided.as_(str, default="logs/data_parser.log"),
        data_sources_path=config.data_sources_path.provided.as_(str, default="../Data_Sources"),
        configs_path=config.configs_path.provided.as_(str, default="configs/partners"),
        batch_size=config.batch_size.provided.as_(int, default=1000),
        max_workers=config.max_workers.provided.as_(int, default=4),
        enable_validation=config.enable_validation.provided.as_(bool, default=True),
        debug=config.debug.provided.as_(bool, default=False),
        dry_run=config.dry_run.provided.as_(bool, default=False)
    )
    
    # Core services
    parser_factory: providers.Provider[IParserFactory] = providers.Singleton(ParserFactory)
    
    data_transformer: providers.Provider[IDataTransformer] = providers.Singleton(DataTransformer)
    
    database_service: providers.Provider[IDatabaseService] = providers.Singleton(DatabaseService)
    
    config_service: providers.Provider[IConfigService] = providers.Singleton(
        ConfigService,
        configs_path=app_config.provided.configs_path
    )
    
    # Main processing service
    data_processing_service = providers.Singleton(
        DataProcessingService,
        parser_factory=parser_factory,
        data_transformer=data_transformer,
        database_service=database_service,
        config_service=config_service
    )


def create_container() -> ApplicationContainer:
    """Create and configure the application container."""
    container = ApplicationContainer()
    
    # Load configuration from environment variables
    container.config.from_dict({
        'db_host': os.getenv('DB_HOST', 'localhost'),
        'db_port': int(os.getenv('DB_PORT', '5432')),
        'db_name': os.getenv('DB_NAME', 'food_tech_analytics'),
        'db_user': os.getenv('DB_USER', 'postgres'),
        'db_password': os.getenv('DB_PASSWORD', ''),
        'db_schema': os.getenv('DB_SCHEMA', 'public'),
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
        'log_file_path': os.getenv('LOG_FILE_PATH', 'logs/data_parser.log'),
        'data_sources_path': os.getenv('DATA_SOURCES_PATH', '../Data_Sources'),
        'configs_path': os.getenv('CONFIGS_PATH', 'configs/partners'),
        'batch_size': int(os.getenv('BATCH_SIZE', '1000')),
        'max_workers': int(os.getenv('MAX_WORKERS', '4')),
        'enable_validation': os.getenv('ENABLE_VALIDATION', 'true').lower() == 'true',
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'dry_run': os.getenv('DRY_RUN', 'false').lower() == 'true'
    })
    
    return container 