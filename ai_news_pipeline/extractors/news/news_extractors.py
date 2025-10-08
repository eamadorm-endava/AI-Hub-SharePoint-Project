import feedparser
import pandas as pd
from typing import Type

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
            - publish_date
        The news retrieved are filtered based in case_sen_search_kw and case_insen_search_kw

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

    def _filter_by_keywords(self) -> list[dict]:
        pass

    def _filter_by_age(self) -> pd.DataFrame:
        pass

    def extract(self) -> pd.DataFrame:
        pass

    def store_to_excel(self) -> None:
        pass
