"""Basic tests to verify project setup."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_imports():
    """Test that all modules can be imported."""
    # Configuration
    from src.config.models import PartnerConfig, AppConfig
    
    # Interfaces
    from src.interfaces.parser_interface import IFileParser, IParserFactory
    from src.interfaces.data_interfaces import IDataTransformer, IDataValidator, IDatabaseService, IConfigService
    
    # Implementations
    from src.parsers.excel_parser import ExcelParser
    from src.parsers.csv_parser import CSVParser
    from src.parsers.parser_factory import ParserFactory
    from src.transformers.data_transformer import DataTransformer
    from src.validators.data_validator import DataValidator
    from src.services.config_service import ConfigService
    from src.services.database_service import DatabaseService
    from src.services.data_processing_service import DataProcessingService
    
    # Container
    from src.container import ApplicationContainer, create_container
    
    print("✓ All imports successful")


def test_config_models():
    """Test configuration model validation."""
    from src.config.models import PartnerConfig, ColumnMapping, SheetConfig, SourceConfig
    
    # Test valid configuration
    config_data = {
        "partner_id": "test_partner",
        "partner_name": "Test Partner",
        "template_id": "test_v1",
        "source_config": {
            "file_format": "excel",
            "sheets_config": [
                {
                    "sheet_name": "Test Sheet",
                    "target_table": "test_table",
                    "column_mappings": [
                        {
                            "source_column": "Test Column",
                            "system_column": "test_column",
                            "column_type": "string",
                            "required": True
                        }
                    ]
                }
            ]
        }
    }
    
    # This should not raise an exception
    partner_config = PartnerConfig(**config_data)
    assert partner_config.partner_id == "test_partner"
    print("✓ Configuration models working")


def test_container():
    """Test dependency injection container."""
    from src.container import create_container
    import os
    
    # Set minimal environment variables
    os.environ['DB_PASSWORD'] = 'test_password'
    
    container = create_container()
    
    # Test that we can get services
    config_service = container.config_service()
    parser_factory = container.parser_factory()
    data_transformer = container.data_transformer()
    
    assert config_service is not None
    assert parser_factory is not None
    assert data_transformer is not None
    
    print("✓ Dependency injection container working")


def test_parser_factory():
    """Test parser factory."""
    from src.parsers.parser_factory import ParserFactory
    from pathlib import Path
    
    factory = ParserFactory()
    
    # Test Excel parser
    excel_parser = factory.get_parser(Path("test.xlsx"))
    assert excel_parser is not None
    assert "ExcelParser" in str(type(excel_parser))
    
    # Test CSV parser
    csv_parser = factory.get_parser(Path("test.csv"))
    assert csv_parser is not None
    assert "CSVParser" in str(type(csv_parser))
    
    # Test unsupported format
    unsupported_parser = factory.get_parser(Path("test.txt"))
    assert unsupported_parser is None
    
    print("✓ Parser factory working")


if __name__ == "__main__":
    print("Running basic tests...")
    
    try:
        test_imports()
        test_config_models()
        test_container()
        test_parser_factory()
        
        print("\n🎉 All basic tests passed! Project setup is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 