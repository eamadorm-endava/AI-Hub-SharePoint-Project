from loguru import logger
import hashlib
from datetime import datetime, timezone

from utils.gcp.bigquery import insert_rows

from .bq_base import BigQueryTable
from database.schemas import NewsMetadata
from agent.config import GCPConfig


gcp_config = GCPConfig()


class NewsExtractionTable(BigQueryTable):
    __name: str = gcp_config.NEWS_EXTRACTION_TABLE_ID
    __primary_key: str = gcp_config.NEWS_EXTRACTION_TABLE_PK

    @property
    def name(self):
        return self.__name

    @property
    def primary_key(self):
        return self.__primary_key

    def _generate_id(self, news_link: str) -> str:
        """
        Generate a valid id from the News Metadata Table.
        Validation of the parameter is not set here, as it will be validated by a
        pydantic schema

        Args:
            news_link: str -> Link of the news

        Returns:
            str -> ID of the row
        """
        return hashlib.sha256(news_link.encode("utf-8")).hexdigest()

    def _insert_row(self, news_metadata: NewsMetadata) -> None:
        """
        Main logic to insert a row in this table

        Args:
            news_metadata: NewsMetadata -> Class containing all the necessary data by the table

        Returns:
            None
        """
        news_metadata.extracted_at = datetime.now(timezone.utc)

        try:
            insert_rows(
                table_name=self.name,
                dataset_name=self.dataset_id,
                project_id=self.project_id,
                rows=[
                    news_metadata.model_dump(exclude_none=True),
                ],
            )

        except Exception as e:
            logger.error(f"Error while inserting news metadata into BigQuery: {e}")

    def add_row(self, news_metadata: NewsMetadata) -> str:
        """
        Orchestrates the steps to add a row to the table

        Args:
            news_metadata: NewsMetadata -> Class containing the necessary parameters which its validators

        Returns:
            str: ID of the news inserted
        """

        logger.debug("Generating ID...")
        news_metadata.news_id = self._generate_id(news_metadata.news_link)

        logger.debug("Adding news to the database...")
        if not self._id_in_table(
            primary_key_column_name=self.primary_key,
            primary_key_row_value=news_metadata.news_id,
            table_name=self.name,
        ):
            logger.warning(
                f"Extracted news {news_metadata.title} already in database, skipping it..."
            )

        else:
            self._insert_row(news_metadata=news_metadata)

        return news_metadata.news_id

    def add_rows(self, list_news_metadata: list[NewsMetadata]) -> None:
        """
        Insert multiple rows in BigQuery at once

        Args:
            list_news_metadata: list[NewsMetadata] -> List of NewsMetadata objects

        Returns:
            None
        """
        if not isinstance(list_news_metadata, list) or not all(
            isinstance(data, NewsMetadata) for data in list_news_metadata
        ):
            logger.error(
                "The parameter list_news_metadata must be a list of NewsMetadata objects"
            )

        # Adding fields that are filled once the data is up to be ingested into the database
        news_to_add = [
            news_metadata.model_copy(
                update={
                    "news_id": self._generate_id(news_metadata.news_link),
                    "extracted_at": datetime.now(timezone.utc),
                }
            ).model_dump()  # To convert NewsMetadata in a Python dictionary
            for news_metadata in list_news_metadata
            # Due to this condition is evaluated before the news_id is created in the NewsMetadata instance
            # it is required to generate the id instead of calling news_metadata.news_id (at that moment is always None)
            if not self._id_in_table(
                primary_key_column_name=self.primary_key,
                primary_key_row_value=self._generate_id(news_metadata.news_link),
                table_name=self.name,
            )
        ]

        if not news_to_add:
            logger.warning("All the news has been previously added to the database.")
            return

        logger.info(
            f"Inserting {len(news_to_add)} new rows into BigQuery table {self.name}"
        )
        try:
            insert_rows(
                table_name=self.name,
                dataset_name=self.dataset_id,
                project_id=self.project_id,
                rows=news_to_add,
            )

        except Exception as e:
            logger.error(f"Error while inserting rows into BigQuery: {e}")
