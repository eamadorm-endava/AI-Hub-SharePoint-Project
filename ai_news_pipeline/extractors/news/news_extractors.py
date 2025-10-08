import feedparser
import pandas as pd
from loguru import logger
from typing import Type, Optional

from ai_news_pipeline.config import AINewsConfig
from ai_news_pipeline.extractors.image_url.extractor_selector import (
    ImageExtractorSelector,
)
from ai_news_pipeline.extractors.image_url.image_url_extractors import (
    BaseImageExtractor,
)
from utils.io_utils import store_df_to_excel

news_config = AINewsConfig()


class NewsExtractor:
    __img_extr_selector: ImageExtractorSelector = ImageExtractorSelector()

    def __init__(
        self,
        feed_url: str,
        case_sen_search_kw: list[str] = news_config.CASE_SEN_SEARCH_KW,
        case_insen_search_kw: list[str] = news_config.CASE_INSEN_SEARCH_KW,
        max_days_old: int = news_config.MAX_DAYS_OLD,
    ):
        """
        Initializes a NewsExtractor instance.

        Args:
            feed_url: str → RSS-compatible URL to retrieve news articles from.
            case_sen_search_kw: list[str] → Case-sensitive keywords for filtering titles.
            case_insen_search_kw: list[str] → Case-insensitive keywords for filtering titles.
            max_days_old: int → Maximum age (in days) allowed for articles.
        """
        self.feed_url: str = feed_url
        self.case_sen_search_kw: list[str] = case_sen_search_kw
        self.case_insen_search_kw: list[str] = case_insen_search_kw
        self.__img_extractor: Type[BaseImageExtractor] = (
            self.__img_extr_selector.get_extractor(self.feed_url)
        )
        self.max_days_old: int = max_days_old
        self.current_data: Optional[pd.DataFrame] = None

    def __articles_extracted(self) -> bool:
        """
        Verifies if self.current_data is not empty
        """
        if not isinstance(self.current_data, pd.DataFrame):
            return False

        return True

    def _get_articles(self) -> None:
        """
        Retrieves AI-related news data in its raw format from the feed_url. The data obtained per news is:
            - title
            - news_link
            - image_link
            - publish_date

        The data obtained is stored in self.current_data

        Returns:
            None
        """
        try:
            feed = feedparser.parse(self.feed_url)

        except Exception as e:
            logger.error(f"Articles from {self.feed_url} could not be extracted: {e}")

        extracted_articles = [
            {
                "title": entry.title.replace("’", "").replace(
                    "'", ""
                ),  # To avoid issues
                "news_link": entry.link,
                "image_link": self.__img_extractor.extract(entry.link)
                if self.__img_extractor
                else None,
                "publish_date": entry.published,
            }
            for entry in feed.entries
        ]

        if extracted_articles:
            logger.info(f"{len(extracted_articles)} articles extracted")
            articles = pd.DataFrame(extracted_articles)

            articles.publish_date = pd.to_datetime(articles.publish_date)

            self.current_data = articles

        else:
            logger.error(
                f"No articles extracted from {self.feed_url} "
                " Make sure the url is RSS-compatible"
            )

    def _filter_title_by_keywords(
        self,
        case_sen_search_kw: Optional[list[str]] = None,
        case_insen_search_kw: Optional[list[str]] = None,
    ) -> None:
        """
        News titles in self.current_data are filtered based in
        case sensitive and case insensitive keywords

        Args:
            case_sen_search_kw: Optional[list[str]] -> List of Case Sensitive Search Keywords.
                                            Default: self.case_sen_search_kw
            case_insen_search_kw: Optional[list[str]] -> List of (Case Insensitive Search Keywords)
                                            Default: self.case_insen_search_kw

        Returns:
            None
        """
        if not case_sen_search_kw:
            case_sen_search_kw = self.case_sen_search_kw

        if not case_insen_search_kw:
            case_insen_search_kw = self.case_insen_search_kw

        if not self.__articles_extracted():
            logger.error(
                "No data found. Please run '_get_articles()' before "
                "calling this method."
            )
            return

        logger.info("Filtering articles by the next parameters...")
        logger.info(f"{case_sen_search_kw =}")
        logger.info(f"{case_insen_search_kw =}")

        initial_data = self.current_data

        def matches_keyword(text: str) -> bool:
            match = any(kw in text for kw in case_sen_search_kw) | any(
                kw.lower() in text.lower() for kw in case_insen_search_kw
            )

            return match

        filtered_data = initial_data[initial_data.title.apply(matches_keyword)]

        # Reset dataframe index to keep sequential order
        filtered_data.reset_index(drop=True)

        self.current_data = filtered_data.reset_index(drop=True)
        logger.info(
            f"Keyword filtering complete. {len(self.current_data)} articles "
            "matched the criteria."
        )

    def _filter_by_age(self, max_days_old: Optional[int] = None) -> None:
        """
        Filters the articles by age since its publication date

        Args:
            max_days_old: Optional[int] -> Maximum days old an article must have to keep it

        Returns:
            None
        """
        if not max_days_old:
            max_days_old = self.max_days_old

        if not self.__articles_extracted():
            logger.error(
                "No data found. Please run '_get_articles()' before "
                "calling this method."
            )
            return

        logger.info(
            f"Filtering articles published within the last {max_days_old} days."
        )

        initial_data = self.current_data

        # As publish_date is in UTC, the current_date must also be in this timezone
        current_date = pd.Timestamp.utcnow()
        max_publish_date = current_date - pd.Timedelta(days=max_days_old)

        filtered_data = initial_data[initial_data.publish_date >= max_publish_date]

        # Reset dataframe index to keep sequential order
        filtered_data.reset_index(drop=True)

        self.current_data = filtered_data
        logger.info(
            f"Date filtering complete. {len(self.current_data)} articles "
            "published within the allowed range."
        )

    def _store_to_excel(
        self,
        local_file_path: str = None,
        sheet_name: str = None,
        table_name: str = None,
    ) -> None:
        if not local_file_path:
            local_file_path = news_config.FILE_PATH

        if not sheet_name:
            sheet_name = news_config.EXCEL_SHEET_NAME

        if not table_name:
            table_name = news_config.EXCEL_TABLE_NAME

        if not self.__articles_extracted():
            logger.error(
                "No data found. Please run '_get_articles()' before "
                "calling this method."
            )
            return

        initial_data = self.current_data.copy()
        # Converting datetime types to strings
        initial_data["publish_date_str"] = initial_data.publish_date.dt.strftime(
            r"%Y-%m-%d %H:%M:%SZ"
        )

        # Deleting publish_date, as is the datetime column that will be replaced
        initial_data.drop("publish_date", axis=1, inplace=True)

        # Renaming publish_date_str to publish_date, this is because it will raise an error
        # if I directly convert publish_date to str
        initial_data.rename(columns={"publish_date_str": "publish_date"}, inplace=True)

        # The function below already has error handlers for the parameters
        store_df_to_excel(
            df=initial_data,
            local_file_path=local_file_path,
            sheet_name=sheet_name,
            table_name=table_name,
        )
        logger.info("Articles successfully stored")

    def extract(
        self,
        case_sen_search_kw: Optional[list[str]] = None,
        case_insen_search_kw: Optional[list[str]] = None,
        max_days_old: Optional[int] = None,
        local_file_path: str = None,
        sheet_name: str = None,
        table_name: str = None,
        store_data: bool = True,
    ) -> None:
        """
        Main orchestration method for extracting, filtering, and optionally storing news articles.

        Steps:
            1. Retrieve articles from the feed URL.
            2. Filter by title keywords (case-sensitive and case-insensitive).
            3. Filter by publish date (based on max_days_old).
            4. Optionally store the final dataset to Excel.

        Args:
            case_sen_search_kw: Optional[list[str]] → Override for case-sensitive keywords.
            case_insen_search_kw: Optional[list[str]] → Override for case-insensitive keywords.
            max_days_old: Optional[int] → Override for maximum article age.
            local_file_path: Optional[str] → Path to save the Excel file.
            sheet_name: Optional[str] → Name of the Excel sheet.
            table_name: Optional[str] → Name of the Excel table.
            store_data: bool → Whether to store the filtered data to Excel.
        Returns:
            None
        """
        logger.info("Starting articles extraction...")
        # Step 1: Retrive all the available articles from the feed_url introduced
        # when instanciating this class
        self._get_articles()

        # Step 2: Filter articles by keywords
        self._filter_title_by_keywords(
            case_sen_search_kw=case_sen_search_kw,
            case_insen_search_kw=case_insen_search_kw,
        )

        # Step 3: Filter articles by publish date
        self._filter_by_age(max_days_old=max_days_old)

        # Step 4: if store_data

        if store_data:
            self._store_to_excel(
                local_file_path=local_file_path,
                sheet_name=sheet_name,
                table_name=table_name,
            )
        else:
            logger.info("No data was stored in an excel file")

        logger.info("Articles extraction completed")
