from loguru import logger
import re
from typing import Optional
from ai_news_pipeline.extractors.image_url.image_url_extractors import (
    BaseImageExtractor,
    AINEWSImageExtractor,
    MITImageExtractor,
)

from ai_news_pipeline.config import AINewsConfig

news_config = AINewsConfig()


class ImageExtractorSelector:
    __base_url_pattern: str = news_config.BASE_URL_PATTERN

    def __init__(self, news_url: str):
        self.news_url = news_url
        self.base_url = self._get_base_url(url=self.news_url)
        self.__extractors = self.__define_extractors()

    @property
    def extractors(self) -> dict[str, type[BaseImageExtractor]]:
        return self.__extractors

    def __define_extractors(self) -> dict[str, type[BaseImageExtractor]]:
        """
        Creates an attibute containing all the extractors registered.

        Returns:
            None
        """
        # BaseImageExtractors are not instanciated
        registered_extractors = {
            self._get_base_url(news_config.AI_NEWS_FEED_URL): AINEWSImageExtractor,
            self._get_base_url(news_config.MIT_NEWS_FEED_URL): MITImageExtractor,
        }

        return registered_extractors

    def _get_base_url(self, url: str) -> str:
        """
        Get the base_url from any url. Ex. news_url 'https://www.news.com/news_article1/' retrieves
        'https://www.news.com'

        Args: url: str -> URL of the page

        Return:
            str -> Link to the base url
        """
        return re.search(self.__base_url_pattern, url).group().rstrip("/")

    def get_image_extractor(self) -> Optional[BaseImageExtractor]:
        """
        Based on the extractors selected and the news_url introduced, retrieves
        a BaseImageExtractor instance

        Returns:
            Optional[BaseImageExtractor]: An instance of a BaseImageExtractor the right one is found
        """
        extractor = self.extractors.get(self.base_url, None)

        if not extractor:
            logger.error(f"No extractor found for the news url: {self.news_url}")
            return None

        logger.info(
            f"Extractor '{extractor.__name__}' selected for base URL: {self.base_url}"
        )
        return extractor(self.news_url)
