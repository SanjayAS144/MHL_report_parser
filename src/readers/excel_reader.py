from pathlib import Path
from typing import Dict, Any, List

from Util.constants import FILE_NAME, SHEET_CONFIG, SHEET_NAME, SOURCE_CONFIG, COLUMN_MAPPING, HEADER_COLUMNS
from interfaces.reader_interface import BaseReader

import pandas as pd
import os

from parsers.base_parser import BaseParser


class ExcelReader(BaseReader):
    def __init__(self, file_path: Path, config: Dict[str, Any]):
        super().__init__(file_path, config)

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the given file."""
        return file_path.suffix.lower() in ['.xlsx', '.xls']

    def read(self) -> List[pd.DataFrame]:
        result = []
        missing_sheets = []
        source_configs = self._config[SOURCE_CONFIG]
        for source_config in source_configs:
            file_name = Path(source_config.get(FILE_NAME))
            sheets_config = source_config.get(SHEET_CONFIG)
            file_path = os.path.join(self._file_path, file_name)

            # Read all sheets from the Excel file
            sheets = pd.read_excel(file_path, sheet_name=None)

            for sheet_cfg in sheets_config:
                sheet_name = sheet_cfg.get(SHEET_NAME)

                if sheet_name not in sheets:
                    missing_sheets.append(file_path + '_' + sheet_name)
                    continue

                df = sheets[sheet_name]
                df = self._realign_header(df, sheet_cfg.get(HEADER_COLUMNS))
                df = self._parse(df, sheet_cfg.get(COLUMN_MAPPING))
                result.append(df)

        return result


    def _parse(self, df: pd.DataFrame, config) -> pd.DataFrame:
        return BaseParser(df, config).parse()


with open('sample.json') as f:
    import json
    inp = json.load(f)
    x = ExcelReader("/Users/naman/workspace/MHL_report_parser/src/readers", inp).read()