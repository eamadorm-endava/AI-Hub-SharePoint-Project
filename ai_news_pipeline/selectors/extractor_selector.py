from loguru import logger
import re
from typing import Optional, Type
from ai_news_pipeline.extractors.image_url.image_url_extractors import (
    BaseImageExtractor,
    AINEWSImageExtractor,
    MITImageExtractor,
)

from ai_news_pipeline.config import AINewsConfig

news_config = AINewsConfig()


class ImageExtractorSelector:
    __base_url_pattern: str = news_config.BASE_URL_PATTERN

    def __init__(self):
        self.__extractors = self.__define_extractors()

    @property
    def extractors(self) -> dict[str, type[BaseImageExtractor]]:
        return self.__extractors

    def __define_extractors(self) -> dict[str, Type[BaseImageExtractor]]:
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
        Get the base_url from any url.
        Example -> 'https://www.news.com/news_article1/' retrieves 'https://www.news.com'

        Args: url: str -> URL of the page

        Return:
            str -> Link to the base url
        """
        return re.search(self.__base_url_pattern, url).group().rstrip("/")

    def get_extractor(self, url: str) -> Optional[BaseImageExtractor]:
        """
        Based on the extractors selected and the url introduced, retrieves
        a BaseImageExtractor instance

        Args:
            url: str -> Link to the news article

        Returns:
            Optional[BaseImageExtractor]: An instance of a BaseImageExtractor the right one is found
        """
        base_url = self._get_base_url(url=url)

        extractor = self.extractors.get(base_url, None)

        if not extractor:
            logger.warning(
                f"No image extractor found for the url: {url}. The data retrieve will not contain an image_url"
            )
            return None

        logger.info(
            f"Extractor '{extractor.__name__}' selected for base URL: {base_url}"
        )
        return extractor()
