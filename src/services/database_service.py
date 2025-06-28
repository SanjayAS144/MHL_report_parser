"""Database service implementation."""

from typing import Any, Dict

import pandas as pd
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..database.connection import get_session
from ..interfaces.data_interfaces import IDatabaseService


class DatabaseService(IDatabaseService):
    """Service for database operations."""
    
    def __init__(self):
        """Initialize database service."""
        logger.info("Database service initialized")
    
    def insert_data(self, df: pd.DataFrame, table_name: str, batch_size: int = 1000) -> bool:
        """
        Insert data into database table.
        
        Args:
            df: DataFrame to insert
            table_name: Target table name
            batch_size: Batch size for insertion
            
        Returns:
            Success status
        """
        if df.empty:
            logger.warning(f"No data to insert into table {table_name}")
            return True
        
        logger.info(f"Inserting {len(df)} rows into table {table_name}")
        
        session: Session = get_session()
        try:
            # Insert data in batches
            total_rows = len(df)
            for start_idx in range(0, total_rows, batch_size):
                end_idx = min(start_idx + batch_size, total_rows)
                batch_df = df.iloc[start_idx:end_idx]
                
                # Convert DataFrame to dictionary records
                records = batch_df.to_dict('records')
                
                # Insert batch
                self._insert_batch(session, table_name, records)
                
                logger.debug(f"Inserted batch {start_idx}-{end_idx} into {table_name}")
            
            session.commit()
            logger.info(f"Successfully inserted {total_rows} rows into {table_name}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to insert data into {table_name}: {e}")
            return False
        finally:
            session.close()
    
    def get_existing_records(self, table_name: str, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Get existing records from table with filters.
        
        Args:
            table_name: Table to query
            filters: Filter conditions
            
        Returns:
            DataFrame with existing records
        """
        session: Session = get_session()
        try:
            # Build query
            query = f"SELECT * FROM {table_name}"
            params = {}
            
            if filters:
                where_conditions = []
                for key, value in filters.items():
                    where_conditions.append(f"{key} = :{key}")
                    params[key] = value
                
                if where_conditions:
                    query += " WHERE " + " AND ".join(where_conditions)
            
            # Execute query
            result_df = pd.read_sql(query, session.bind, params=params)
            
            logger.debug(f"Retrieved {len(result_df)} records from {table_name}")
            return result_df
            
        except Exception as e:
            logger.error(f"Failed to get records from {table_name}: {e}")
            return pd.DataFrame()
        finally:
            session.close()
    
    def create_tables(self) -> bool:
        """Create all required tables in database."""
        try:
            from ..database.connection import get_database_connection
            db_connection = get_database_connection()
            return db_connection.create_tables()
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def _insert_batch(self, session: Session, table_name: str, records: list):
        """Insert a batch of records into the database."""
        try:
            # Get table object from metadata
            from ..database.models import Base
            table = Base.metadata.tables.get(table_name)
            
            if table is None:
                raise ValueError(f"Table {table_name} not found in metadata")
            
            # Insert records
            session.execute(table.insert(), records)
            
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error inserting batch into {table_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inserting batch into {table_name}: {e}")
            raise