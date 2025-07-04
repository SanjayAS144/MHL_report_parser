# Food Tech Analytics Data Parser

A comprehensive data parsing and ingestion system for food tech analytics platforms. This system provides a generic, configuration-driven approach to parse data from various food delivery partners and populate a standardized PostgreSQL database.

## Features

- **Generic Parser Framework**: Supports Excel, CSV, and JSON file formats
- **Configuration-Driven**: Easy partner onboarding through JSON configuration files
- **Dependency Injection**: Modular architecture with clear separation of concerns
- **Data Validation**: Comprehensive validation using Pydantic models
- **Error Handling**: Robust error handling with detailed logging
- **Database Integration**: Direct PostgreSQL integration with SQLAlchemy ORM
- **Batch Processing**: Efficient batch processing for large datasets

## Architecture

```
src/
├── interfaces/          # Abstract interfaces
├── services/           # Business logic services
├── parsers/           # File parsing implementations
├── transformers/      # Data transformation logic
├── validators/        # Data validation
├── database/          # Database models and operations
└── config/           # Configuration management

configs/
└── partners/         # Partner-specific configurations

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── fixtures/        # Test data
```

## Setup

1. **Clone and Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Database Setup**
```bash
# Create PostgreSQL database
createdb food_tech_analytics
```

3. **Environment Configuration**
```bash
# Copy and configure environment file
cp env_template.txt .env
# Edit .env with your database credentials
```

4. **Initialize Database Schema**
```bash
python -m src.database.schema_creator
```

## Usage

### Basic Usage
```bash
# Parse all partners
python main.py parse-all

# Parse specific partner
python main.py parse-partner --partner-id zomato

# Dry run (validation only)
python main.py parse-all --dry-run
```

### Adding New Partners

1. Create partner configuration in `configs/partners/{partner_id}.json`
2. Add sample data files for testing
3. Run validation: `python main.py validate-config --partner-id {partner_id}`

## Configuration Format

Each partner requires a JSON configuration file:

```json
{
  "partner_id": "zomato",
  "partner_name": "Zomato",
  "template_id": "zomato_v1",
  "source_config": {
    "file_format": "excel",
    "sheets_config": [
      {
        "sheet_name": "Orders",
        "target_table": "orders",
        "headers_row": 1,
        "column_mappings": [
          {
            "source_column": "Order ID",
            "system_column": "order_id",
            "column_type": "string",
            "required": true
          }
        ]
      }
    ]
  }
}
```

## Database Schema

The system uses a normalized database schema with 4 logical schemas:
- `platform_management`: Partners, outlets, brands
- `transaction_processing`: Orders, payments, items
- `customer_experience`: Feedback, campaigns
- `analytics_reporting`: Metrics, reports

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
black src/
isort src/
flake8 src/
mypy src/
```

## Contributing

1. Follow the existing code structure
2. Add appropriate tests for new features
3. Update configuration documentation
4. Ensure all quality checks pass

## License

MIT License #   M H L _ r e p o r t _ p a r s e r  
 