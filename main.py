"""Main CLI application."""

import os
import sys
from pathlib import Path

import click
from dotenv import load_dotenv
from loguru import logger

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.container import create_container


def setup_logging(log_level: str, log_file: str):
    """Setup logging configuration."""
    logger.remove()  # Remove default handler
    
    # Console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # File handler
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True) 
    
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days"
    )


@click.group()
@click.option('--config-file', type=click.Path(), help='Configuration file path')
@click.option('--log-level', default='INFO', help='Logging level')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def cli(ctx, config_file, log_level, debug):
    """Food Tech Analytics Data Parser CLI."""
    # Load environment variables
    if config_file and Path(config_file).exists():
        load_dotenv(config_file)
    else:
        load_dotenv()  # Load from .env file if exists
    
    # Override log level if debug is enabled
    if debug:
        log_level = 'DEBUG'
        os.environ['DEBUG'] = 'true'
    
    # Setup logging
    log_file = os.getenv('LOG_FILE_PATH', 'logs/data_parser.log')
    setup_logging(log_level, log_file)
    
    # Create container
    container = create_container()
    ctx.ensure_object(dict)
    ctx.obj['container'] = container
    
    logger.info("Food Tech Analytics Data Parser initialized")


@cli.command()
@click.option('--partner-id', required=True, help='Partner ID to process')
@click.option('--dry-run', is_flag=True, help='Validate only, do not insert to database')
@click.pass_context
def parse_partner(ctx, partner_id, dry_run):
    """Parse data for a specific partner."""
    container = ctx.obj['container']
    
    try:
        # Get services
        data_processing_service = container.data_processing_service()
        app_config = container.app_config()
        
        # Override dry_run if specified
        if dry_run:
            os.environ['DRY_RUN'] = 'true'
        
        logger.info(f"Starting data processing for partner: {partner_id}")
        
        # Process partner data
        result = data_processing_service.process_partner_data(
            partner_id=partner_id,
            data_sources_path=app_config.data_sources_path,
            dry_run=dry_run or app_config.dry_run
        )
        
        # Display results
        click.echo(f"\nProcessing Results for {partner_id}:")
        click.echo(f"Success: {result['success']}")
        click.echo(f"Files processed: {result['files_processed']}")
        click.echo(f"Records processed: {result['records_processed']}")
        
        if result['warnings']:
            click.echo(f"\nWarnings:")
            for warning in result['warnings']:
                click.echo(f"  - {warning}")
        
        if result['errors']:
            click.echo(f"\nErrors:")
            for error in result['errors']:
                click.echo(f"  - {error}")
            sys.exit(1)
        
        click.echo("\nProcessing completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to process partner {partner_id}: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--dry-run', is_flag=True, help='Validate only, do not insert to database')
@click.pass_context
def parse_all(ctx, dry_run):
    """Parse data for all configured partners."""
    container = ctx.obj['container']
    
    try:
        # Get services
        data_processing_service = container.data_processing_service()
        app_config = container.app_config()
        
        # Override dry_run if specified
        if dry_run:
            os.environ['DRY_RUN'] = 'true'
        
        logger.info("Starting data processing for all partners")
        
        # Process all partners
        results = data_processing_service.process_all_partners(
            data_sources_path=app_config.data_sources_path,
            dry_run=dry_run or app_config.dry_run
        )
        
        # Display results
        click.echo(f"\nProcessing Results:")
        click.echo(f"{'Partner':<15} {'Success':<8} {'Files':<6} {'Records':<8} {'Errors':<6}")
        click.echo("-" * 50)
        
        total_files = 0
        total_records = 0
        successful_partners = 0
        
        for result in results:
            success_marker = "✓" if result['success'] else "✗"
            error_count = len(result['errors'])
            
            click.echo(f"{result['partner_id']:<15} {success_marker:<8} {result['files_processed']:<6} "
                      f"{result['records_processed']:<8} {error_count:<6}")
            
            total_files += result['files_processed']
            total_records += result['records_processed']
            if result['success']:
                successful_partners += 1
        
        click.echo("-" * 50)
        click.echo(f"Total: {successful_partners}/{len(results)} partners successful, "
                  f"{total_files} files, {total_records} records processed")
        
        # Show detailed errors if any
        has_errors = any(result['errors'] for result in results)
        if has_errors:
            click.echo(f"\nDetailed Errors:")
            for result in results:
                if result['errors']:
                    click.echo(f"\n{result['partner_id']}:")
                    for error in result['errors']:
                        click.echo(f"  - {error}")
        
        if has_errors:
            sys.exit(1)
        else:
            click.echo("\nAll processing completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to process partners: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--partner-id', required=True, help='Partner ID to validate')
@click.pass_context
def validate_config(ctx, partner_id):
    """Validate partner configuration."""
    container = ctx.obj['container']
    
    try:
        config_service = container.config_service()
        
        logger.info(f"Validating configuration for partner: {partner_id}")
        
        # Load and validate configuration
        config = config_service.load_partner_config(partner_id)
        validation_result = config_service.validate_config(config)
        
        click.echo(f"\nValidation Results for {partner_id}:")
        click.echo(f"Valid: {validation_result['valid']}")
        
        if validation_result['errors']:
            click.echo(f"\nErrors:")
            for error in validation_result['errors']:
                click.echo(f"  - {error['field']}: {error['message']}")
        
        if validation_result['warnings']:
            click.echo(f"\nWarnings:")
            for warning in validation_result['warnings']:
                click.echo(f"  - {warning}")
        
        if validation_result['valid']:
            click.echo("\nConfiguration is valid!")
        else:
            click.echo("\nConfiguration has errors!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to validate configuration for {partner_id}: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def list_partners(ctx):
    """List all configured partners."""
    container = ctx.obj['container']
    
    try:
        config_service = container.config_service()
        partners = config_service.list_partners()
        
        if not partners:
            click.echo("No partner configurations found.")
            return
        
        click.echo(f"\nConfigured Partners ({len(partners)}):")
        for partner in partners:
            click.echo(f"  - {partner}")
        
    except Exception as e:
        logger.error(f"Failed to list partners: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def create_tables(ctx):
    """Create database tables."""
    container = ctx.obj['container']
    
    try:
        database_service = container.database_service()
        
        logger.info("Creating database tables")
        success = database_service.create_tables()
        
        if success:
            click.echo("Database tables created successfully!")
        else:
            click.echo("Failed to create database tables!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli() 