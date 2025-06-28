from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from Util.util import clean_df_rows, clean_dataframe_columns


class BaseReader(ABC):
    """
    Abstract base class for file readers.
    """

    def __init__(self, file_path: Path, config: Dict[str, Any]):
        self._file_path = file_path
        self._config = config

    @abstractmethod
    def can_parse(self, file_path: Path) -> bool:
        """
        Check if the reader can parse the given file.
        """
        pass

    @abstractmethod
    def read(self) -> Dict[str, pd.DataFrame]:
        """
        Read the file and return a dictionary of DataFrames.
        """
        pass

    def _find_header_row_index(self, df: pd.DataFrame, expected_columns: list) -> int:
        for idx, row in df.iterrows():
            if list(row.astype(str).str.strip()) == expected_columns:
                return idx
        raise ValueError("Header row not found.")

    def _realign_header(self, df: pd.DataFrame, expected_columns: list) -> pd.DataFrame:
        df = clean_dataframe_columns(df)
        columns = df.columns.tolist()
        df = clean_df_rows(df, columns)
        header_idx = self._find_header_row_index(df, expected_columns)
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
        df.columns = expected_columns
        return df