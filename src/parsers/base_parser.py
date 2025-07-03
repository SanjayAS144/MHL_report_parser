from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

class BaseParser:
    """Generic base parser for tabular files."""

    def __init__(self, config, dataframe: pd.DataFrame):
        self._config = config # store single sheet level information like in csv
        self._dataframe = dataframe

    def parse(self) -> pd.DataFrame:
        """
        Common parsing flow shared by all parsers.
        Reads the file and returns a dictionary of DataFrames.
        """
        self._rename_headers(self._config)
        return self._dataframe


    def _get_transformed_mapping_template(self, initial_mapping_template):
        """
        :param initial_mapping_template: dictionary template in the form "{'target_field': ['source_field1', 'source_field2']}"
        :return : dictionary template in the form "{'source_field': 'target_field'}"
        """
        dataframe_cols = self._dataframe.columns
        transformed_mapping_template = {}
        for target_field in initial_mapping_template.keys():
            for source_field in initial_mapping_template[target_field]:
                if source_field in dataframe_cols:
                    transformed_mapping_template[source_field] = target_field
                else:
                    continue
        return transformed_mapping_template

    def _rename_headers(self, mapping_template):
        """
        :param mapping_template: a dictionary with source keys to target keys mapping
        :return: data frame with mapped column names
        """
        self._dataframe.rename(columns=self._get_transformed_mapping_template(mapping_template), inplace=True)
        self.keys = self._dataframe.columns
        return self