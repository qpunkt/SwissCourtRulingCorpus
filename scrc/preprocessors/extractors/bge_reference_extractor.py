from __future__ import annotations
from typing import Any, TYPE_CHECKING, Union
import bs4
import pandas as pd
from sqlalchemy.engine.base import Engine
from root import ROOT_DIR
from scrc.preprocessors.extractors.abstract_extractor import AbstractExtractor
from scrc.utils.main_utils import get_config
from scrc.utils.sql_select_utils import join_decision_and_language_on_parameter, \
    where_decisionid_in_list, where_string_spider, join_file_on_decision

if TYPE_CHECKING:
    from pandas.core.frame import DataFrame


class BgeReferenceExtractor(AbstractExtractor):
    """
    Extracts the reference to a bger from bge header section. This is part of the criticality prediction task.
    """

    def __init__(self, config: dict):
        super().__init__(config, function_name='bge_reference_extracting_functions', col_name='bge_reference')
        self.processed_file_path = self.progress_dir / "bge_reference_extracted.txt"
        self.logger_info = {
            'start': 'Started extracting the bge references',
            'finished': 'Finished extracting the bge references',
            'start_spider': 'Started extracting the bge references for spider',
            'finish_spider': 'Finished extracting the bge references for spider',
            'saving': 'Saving chunk of bge references',
            'processing_one': 'Extracting the bge references from',
            'no_functions': 'Not extracting the bge references'
        }

    def get_database_selection_string(self, spider: str, lang: str) -> str:
        """Returns the `where` clause of the select statement for the entries to be processed by extractor"""
        return f"spider='{spider}' AND header IS NOT NULL AND header <> ''"

    def get_required_data(self, series: pd.DataFrame) -> Union[bs4.BeautifulSoup, str, None]:
        """Returns the data required by the processing functions"""
        """
        html_raw = series['html_raw']
        if pd.notna(html_raw) and html_raw not in [None, '']:
            # Parses the html string with bs4 and returns the body content
            return bs4.BeautifulSoup(html_raw, "html.parser")
        pdf_raw = series['pdf_raw']
        if pd.notna(pdf_raw) and pdf_raw not in [None, '']:
            return pdf_raw
        return None
        """
        return series['section_text']

    def select_df(self, engine: str, spider: str) -> str:
        """Returns the `where` clause of the select statement for the entries to be processed by extractor"""
        only_given_decision_ids_string = f" AND {where_decisionid_in_list(self.decision_ids)}" if self.decision_ids is not None else ""
        """return self.select(engine, f"file {join_decision_and_language_on_parameter('file_id', 'file.file_id')}",
                           f"decision_id, iso_code as language, html_raw, pdf_raw, file_name, 'date', 'extract(year from date) as year', '{spider}' as spider",
                           where=f"file.file_id IN {where_string_spider('file_id', spider)} {only_given_decision_ids_string}",
                           chunksize=self.chunksize)
        """
        #TODO add file_name
        return self.select(engine, f"section {join_decision_and_language_on_parameter('decision_id', 'section.decision_id')} {join_file_on_decision()}", f"section.decision_id, section_text, file_name, '{spider}' as spider, iso_code as language, html_url", where=f"section.section_type_id = 2 AND section.decision_id IN {where_string_spider('decision_id', spider)} {only_given_decision_ids_string}", chunksize=self.chunksize)

    def save_data_to_database(self, df: pd.DataFrame, engine: Engine):
        """Instead of saving data into database, references get written into a text file"""
        self.logger.info("save data in progress")
        path = self.data_dir / 'datasets' / 'criticality_prediction'
        if not path.exists():
            self.create_dir(self.data_dir / 'datasets', 'criticality_prediction')
        processed_file_path = path / "bge_references_found.txt"
        not_processed_file_path = path / "bge_not_extracted.txt"
        for _, row in df.iterrows():
            # only add new content to textfile not overwriting
            if 'bge_reference' in row and row['bge_reference'] != 'no reference found':
                bge_references = str(row['bge_reference'])
                bge_references = bge_references.split("-")
                for item in bge_references:
                    if item != "":
                        bge_file_name = str(row['file_name'])
                        with processed_file_path.open("a") as f:
                            f.write(f"{bge_file_name} {item}\n")

            else:
                with not_processed_file_path.open("a") as f:
                    file_name = str(row['file_name'])
                    f.write(f"{file_name}\n")

    def check_condition_before_process(self, spider: str, data: Any, namespace: dict) -> bool:
        """Override if data has to conform to a certain condition before processing.
        e.g. data is required to be present for analysis"""
        return bool(data)

    def get_coverage(self, spider: str):
        """No coverage implemented"""
        pass


if __name__ == '__main__':
    config = get_config()
    bge_reference_extractor = BgeReferenceExtractor(config)
    # delete bge_reference_found.txt file before letting it run.
    # remove CH_BGE from processed spiders
    bge_reference_extractor.start()
