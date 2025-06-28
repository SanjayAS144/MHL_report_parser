"""Data validation implementation."""

from typing import Any, Dict

import pandas as pd
from loguru import logger

from ..interfaces.data_interfaces import IDataValidator


class DataValidator(IDataValidator):
    """Implementation of data validator."""
    
    def validate(self, df: pd.DataFrame, table_name: str) -> Dict[str, Any]:
        """
        Validate data and return validation results.
        
        Args:
            df: DataFrame to validate
            table_name: Target table name
            
        Returns:
            Validation results with errors and warnings
        """
        logger.debug(f"Validating DataFrame for table: {table_name}")
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'row_count': len(df),
            'column_count': len(df.columns) if not df.empty else 0
        }
        
        if df.empty:
            result['warnings'].append("DataFrame is empty")
            return result
        
        try:
            # Table-specific validations
            if table_name == 'orders':
                self._validate_orders(df, result)
            elif table_name == 'order_items':
                self._validate_order_items(df, result)
            elif table_name == 'payments':
                self._validate_payments(df, result)
            elif table_name == 'settlement_reports':
                self._validate_settlement_reports(df, result)
            elif table_name == 'invoices':
                self._validate_invoices(df, result)
            
            # Generic validations
            self._validate_generic(df, result)
            
            # Set overall validity
            result['valid'] = len(result['errors']) == 0
            
            logger.debug(f"Validation complete for {table_name}: "
                        f"{'PASS' if result['valid'] else 'FAIL'}, "
                        f"{len(result['errors'])} errors, {len(result['warnings'])} warnings")
            
            return result
            
        except Exception as e:
            logger.error(f"Validation failed for table {table_name}: {e}")
            result['valid'] = False
            result['errors'].append(f"Validation error: {e}")
            return result
    
    def _validate_orders(self, df: pd.DataFrame, result: Dict[str, Any]):
        """Validate orders table data."""
        required_columns = ['order_id', 'order_date', 'order_status']
        
        for col in required_columns:
            if col not in df.columns:
                result['errors'].append(f"Required column missing: {col}")
            elif df[col].isna().any():
                null_count = df[col].isna().sum()
                result['errors'].append(f"Column '{col}' has {null_count} null values")
        
        # Check for duplicate order IDs
        if 'order_id' in df.columns:
            duplicates = df['order_id'].duplicated().sum()
            if duplicates > 0:
                result['warnings'].append(f"Found {duplicates} duplicate order IDs")
        
        # Validate order status values
        if 'order_status' in df.columns:
            valid_statuses = ['pending', 'confirmed', 'in_preparation', 'ready', 
                            'out_for_delivery', 'delivered', 'cancelled', 'refunded']
            invalid_statuses = df[~df['order_status'].isin(valid_statuses)]['order_status'].unique()
            if len(invalid_statuses) > 0:
                result['warnings'].append(f"Invalid order statuses found: {list(invalid_statuses)}")
    
    def _validate_order_items(self, df: pd.DataFrame, result: Dict[str, Any]):
        """Validate order items table data."""
        required_columns = ['order_id', 'item_name', 'quantity', 'unit_price']
        
        for col in required_columns:
            if col not in df.columns:
                result['errors'].append(f"Required column missing: {col}")
            elif df[col].isna().any():
                null_count = df[col].isna().sum()
                result['errors'].append(f"Column '{col}' has {null_count} null values")
        
        # Validate numeric fields
        if 'quantity' in df.columns:
            invalid_qty = df[df['quantity'] <= 0]['quantity'].count()
            if invalid_qty > 0:
                result['warnings'].append(f"Found {invalid_qty} items with invalid quantity (<= 0)")
        
        if 'unit_price' in df.columns:
            invalid_price = df[df['unit_price'] < 0]['unit_price'].count()
            if invalid_price > 0:
                result['warnings'].append(f"Found {invalid_price} items with negative unit price")
    
    def _validate_payments(self, df: pd.DataFrame, result: Dict[str, Any]):
        """Validate payments table data."""
        required_columns = ['payment_id', 'order_id', 'payment_method', 'payment_status', 'amount']
        
        for col in required_columns:
            if col not in df.columns:
                result['errors'].append(f"Required column missing: {col}")
            elif df[col].isna().any():
                null_count = df[col].isna().sum()
                result['errors'].append(f"Column '{col}' has {null_count} null values")
        
        # Validate payment amounts
        if 'amount' in df.columns:
            negative_amounts = df[df['amount'] < 0]['amount'].count()
            if negative_amounts > 0:
                result['warnings'].append(f"Found {negative_amounts} payments with negative amounts")
        
        # Validate payment methods
        if 'payment_method' in df.columns:
            valid_methods = ['cash', 'card', 'upi', 'wallet', 'net_banking']
            invalid_methods = df[~df['payment_method'].isin(valid_methods)]['payment_method'].unique()
            if len(invalid_methods) > 0:
                result['warnings'].append(f"Invalid payment methods found: {list(invalid_methods)}")
    
    def _validate_settlement_reports(self, df: pd.DataFrame, result: Dict[str, Any]):
        """Validate settlement reports table data."""
        required_columns = ['settlement_id', 'settlement_date', 'total_amount']
        
        for col in required_columns:
            if col not in df.columns:
                result['errors'].append(f"Required column missing: {col}")
            elif df[col].isna().any():
                null_count = df[col].isna().sum()
                result['errors'].append(f"Column '{col}' has {null_count} null values")
        
        # Validate amounts
        numeric_columns = ['total_amount', 'commission_amount', 'settlement_amount']
        for col in numeric_columns:
            if col in df.columns:
                negative_values = df[df[col] < 0][col].count()
                if negative_values > 0:
                    result['warnings'].append(f"Found {negative_values} negative values in {col}")
    
    def _validate_invoices(self, df: pd.DataFrame, result: Dict[str, Any]):
        """Validate invoices table data."""
        required_columns = ['invoice_number', 'invoice_date', 'total_amount']
        
        for col in required_columns:
            if col not in df.columns:
                result['errors'].append(f"Required column missing: {col}")
            elif df[col].isna().any():
                null_count = df[col].isna().sum()
                result['errors'].append(f"Column '{col}' has {null_count} null values")
        
        # Check for duplicate invoice numbers
        if 'invoice_number' in df.columns:
            duplicates = df['invoice_number'].duplicated().sum()
            if duplicates > 0:
                result['warnings'].append(f"Found {duplicates} duplicate invoice numbers")
    
    def _validate_generic(self, df: pd.DataFrame, result: Dict[str, Any]):
        """Perform generic validations on any DataFrame."""
        # Check for completely empty rows
        empty_rows = df.isna().all(axis=1).sum()
        if empty_rows > 0:
            result['warnings'].append(f"Found {empty_rows} completely empty rows")
        
        # Check for columns with all null values
        null_columns = df.columns[df.isna().all()].tolist()
        if null_columns:
            result['warnings'].append(f"Columns with all null values: {null_columns}")
        
        # Check data types consistency (basic check)
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed data types in object columns
                non_null_values = df[col].dropna()
                if len(non_null_values) > 0:
                    # Simple check for numeric values in string columns
                    numeric_count = pd.to_numeric(non_null_values, errors='coerce').notna().sum()
                    if 0 < numeric_count < len(non_null_values):
                        result['warnings'].append(f"Column '{col}' has mixed data types")
        
        # Check for extremely long strings that might indicate data issues
        for col in df.select_dtypes(include=['object']).columns:
            max_length = df[col].astype(str).str.len().max()
            if max_length > 1000:  # Arbitrary threshold
                result['warnings'].append(f"Column '{col}' has very long values (max: {max_length} chars)") 