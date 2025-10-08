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

news_config = AINewsConfig()


class NewsExtractor:
    __img_extr_selector: ImageExtractorSelector = ImageExtractorSelector()

    def __init__(
        self,
        feed_url: str,
        case_sen_search_kw: list[str] = news_config.CASE_SEN_SEARCH_KW,
        case_insen_search_kw: list[str] = news_config.CASE_INSEN_SEARCH_KW,
    ):
        """
        Instanciates a BaseNewsExtractor object

        Args:
            feed_url: str -> Link of the feed URL where the news will be retrieved from
            case_sen_search_kw list[str] -> List of keywords to search news from (case sensitive)
            case_insen_search_kw list[str] -> List of keywords to search news from (case insensitive)

        """
        self.feed_url: str = feed_url
        self.case_sen_search_kw: list[str] = case_sen_search_kw
        self.case_insen_search_kw: list[str] = case_insen_search_kw
        self.__img_extractor: Type[BaseImageExtractor] = (
            self.__img_extr_selector.get_extractor(self.feed_url)
        )

    def _get_raw_parsed_data(self) -> list[dict]:
        """
        Retrieves AI-related news data in its raw format from the feed_url. The data obtained per news is:
            - title
            - news_link
            - image_link
            - publish_date

        Returns:
            list[dict] -> Each dictionary represents a news retrieved.
        """
        feed = feedparser.parse(self.feed_url)

        news = [
            {
                "title": entry.title.replace("'", ""),
                "news_link": entry.link,
                "image_link": self.__img_extractor.extract(entry.link)
                if self.__img_extractor
                else "",
                "publish_date": entry.published,
            }
            for entry in feed.entries
        ]

        return news

    def _filter_by_keywords(
        self,
        news_extracted: list[dict],
        filter_key: str = "title",
        case_sen_search_kw: list[str] = None,
        case_insen_search_kw: list[str] = None,
    ) -> Optional[list[dict]]:
        """
        News retrieved from _get_raw_parsed_data are filtered based in
        case sensitive and case insensitive keywords

        Args:
            news_extracted: list[dict] -> List of dictionaries where each represents an
                                          article. It must contain at least the
                                          key set in 'filter_key' parameter
            filter_key: str -> Name of the key to filter by. Default: 'title'
            case_sen_search_kw: list[str] -> List of Case Sensitive Search Keywords.
                                            Default: self.case_sen_search_kw
            case_insen_search_kw: list[str] -> List of (Case Insensitive Search Keywords)
                                            Default: self.case_insen_search_kw

        Returns:
            list[dict] -> List of dictionaries filtered
        """
        if not case_sen_search_kw:
            case_sen_search_kw = self.case_sen_search_kw

        if not case_insen_search_kw:
            case_insen_search_kw = self.case_insen_search_kw

        if not isinstance(news_extracted, list):
            logger.error(
                "The parameter news_extracted must be a list of dictionaries. "
                "Each dictionary must, at least, contain the key set in filter_key "
                "(default to 'title')"
            )
            return None

        if not all(isinstance(article, dict) for article in news_extracted):
            logger.error("Each entry of the news_extracted list must be dictionaries")
            return None

        if not all(filter_key in article.keys() for article in news_extracted):
            logger.error(
                "Each dictionary of the news_extracted list must contain the "
                f"filter key: {filter_key}"
            )
            return None

        logger.info("Filtering by the next parameters...")
        logger.info(f"{filter_key = }")
        logger.info(f"{case_sen_search_kw =}")
        logger.info(f"{case_insen_search_kw =}")
        news_filtered = [
            article
            for article in news_extracted
            if any(kw in article.get(filter_key) for kw in case_sen_search_kw)
            or any(
                kw.lower() in article.get(filter_key).lower()
                for kw in case_insen_search_kw
            )
        ]

        return news_filtered

    def _filter_by_age(self) -> pd.DataFrame:
        pass

    def extract(self) -> pd.DataFrame:
        pass

    def store_to_excel(self) -> None:
        pass
