from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
from loguru import logger
from typing import Optional
import re

from ai_news_pipeline.config import AINewsConfig


news_config = AINewsConfig()


class BaseImageExtractor(ABC):
    def __init__(self, url: str):
        self.url: str = url
        self._html_code: Optional[BeautifulSoup] = None

    def _get_html_code(self) -> bool:
        """
        Protected method; retrieves the HTML code from the URL

        Returns:
            bool: True if the retrieval was successfull otherwise False
        """
        if not isinstance(self.url, str):
            raise ValueError(
                "No URL has been introduced. Introduce a string representing the URL."
            )

        # In case the html_code has already been extracted
        if self._html_code:
            return True

        # Build header to get the html from the news_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            self._html_code = BeautifulSoup(response.content, "html.parser")

        except requests.RequestException as e:
            error_message = f"Error fetching html from page {self.url}: {e}"
            logger.error(error_message)
            return False

        return True

    @abstractmethod
    def _get_image_link(self) -> Optional[str]:
        """
        Uses self._html_code to get the link of the main image of the url

        Returns: Optional[str] -> url of the main image if any
        """
        pass

    def extract(self) -> Optional[str]:
        """
        Orchestrates the extraction

        Returns: Optional[str] -> URL of the main image of the url
        """

        if self._get_html_code():
            return self._get_image_link()

        return None


class MITImageExtractor(BaseImageExtractor):
    # Private class attributes
    __news_feed_url: str = news_config.MIT_NEWS_FEED_URL
    __base_url_pattern: str = news_config.BASE_URL_PATTERN

    def __init__(self, news_url: str):
        """
        Creates an instance of the MITImageExtractor class

        Args:
            news_url: str -> Link to an MIT article
        """
        super().__init__(url=news_url)

    # property decorator allows to access a method as if it was an attribute
    # also creates a read-only attribute
    @property
    def news_feed_url(self):
        return self.__news_feed_url

    @property
    def base_url_pattern(self):
        return self.__base_url_pattern

    @property
    def base_url(self):
        return re.search(self.base_url_pattern, self.news_feed_url).group().rstrip("/")

    def _get_image_link(self) -> Optional[str]:
        """
        Get the main image from the MIT site

        Return:
            Optional[str] -> Link to the main image
        """
        try:
            image_tag = self._html_code.find(
                "div", class_="news-article--media--image--file"
            ).find("img")
            image_src = image_tag.get("data-src")
            return self.base_url + image_src

        except Exception as e:
            logger.warning(
                f"Structure to get the image of the url {self.url} was't found: {e}"
            )
            return None


class AINEWSImageExtractor(BaseImageExtractor):
    # Private class attributes
    __news_feed_url: str = news_config.AI_NEWS_FEED_URL
    __base_url_pattern: str = news_config.BASE_URL_PATTERN

    def __init__(self, news_url: str):
        """
        Creates an instance of the AINEWSImageExtractor class

        Args:
            news_url: str -> Link to an AINEWS article
        """
        super().__init__(url=news_url)

    # property decorator allows to access a method as if it was an attribute
    # also creates a read-only attribute
    @property
    def news_feed_url(self):
        return self.__news_feed_url

    @property
    def base_url_pattern(self):
        return self.__base_url_pattern

    @property
    def base_url(self):
        return re.search(self.base_url_pattern, self.news_feed_url).group().rstrip("/")

    def _get_image_link(self) -> Optional[str]:
        """
        Get the main image from the AINEWS article site

        Return:
            Optional[str] -> Link to the main image
        """
        try:
            all_containers = self._html_code.select(".elementor-widget-container")
            containers_with_images = [c for c in all_containers if c.find("img")]
            image_url = [
                container.find("img").get("src")
                for container in containers_with_images
                if container.find("img").get("width") == "800"
            ][0]

            return image_url

        except Exception as e:
            logger.warning(
                f"Structure to get the image of the url {self.url} was't found: {e}"
            )

            return None
