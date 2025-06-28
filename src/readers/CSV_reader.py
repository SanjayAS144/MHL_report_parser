from pathlib import Path
from typing import Dict, Any

from interfaces.reader_interface import BaseReader

import pandas as pd

class CSVReader(BaseReader):
    def __init__(self, file_path: Path, config: Dict[str, Any]):
        super().__init__(file_path, config)


    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.suffix.lower() == '.csv'

    def read(self) -> Dict[str, pd.DataFrame]:
        dataframe = pd.read_csv(self._file_path)

        self._realign_header(dataframe, )
        return [dataframe]

