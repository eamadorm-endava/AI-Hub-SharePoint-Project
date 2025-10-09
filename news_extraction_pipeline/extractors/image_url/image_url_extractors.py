from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import requests
from loguru import logger
from typing import Optional
import re

from news_extraction_pipeline.config import AINewsConfig


news_config = AINewsConfig()


class BaseImageExtractor(ABC):
    # Private class attributes
    __base_url_pattern: str = news_config.BASE_URL_PATTERN
    _feed_url: Optional[str] = None
    _base_feed_url: Optional[str] = None

    def __init__(self):
        self.current_article_url: Optional[str] = None
        self.current_html_code: Optional[BeautifulSoup] = None

    # Called when a subclass is defined (not instanciated)
    # Ensures required subclass-level attributes are present
    def __init_subclass__(cls) -> None:
        """
        Make sure subclasses defines required attributes
        """

        if not cls._feed_url:
            raise NotImplementedError(
                f"{cls.__name__} must define a not null class attribute '_feed_url'"
            )

        # Automatically derive _base_feed_url
        cls._base_feed_url = cls._get_base_url(cls._feed_url)

    @classmethod
    def _get_base_url(cls, url: str) -> str:
        """
        Get the base_url from any url.
        Example -> 'https://www.news.com/news_article1/' retrieves 'https://www.news.com'

        Args: url: str -> URL of the page

        Return:
            str -> Link to the base url
        """
        return re.search(cls.__base_url_pattern, url).group().rstrip("/")

    def _fetch_html_code(self, article_url: str) -> bool:
        """
        Protected method; retrieves the HTML code from the article_url. If the
        extraction was sucessful, stores the html and the article_url as instance attributes

        Args:
            article_url: str -> URL that is required to get its html code
        Returns:
            bool: True if the retrieval was successfull otherwise False
        """
        if not isinstance(article_url, str):
            raise ValueError(
                "No article url has been introduced. Introduce a string representing the URL."
            )

        # In case the html_code has already been extracted
        if self.current_article_url == article_url:
            return True

        elif self._get_base_url(article_url) != self._base_feed_url:
            logger.error(
                f"The URL introduced in article_url: {article_url} does not correspond to the ImageExtractor defined"
            )
            return False

        # Build header to get the html from the news_url
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        try:
            response = requests.get(article_url, headers=headers, timeout=60)
            response.raise_for_status()

            self.current_html_code = BeautifulSoup(response.content, "html.parser")
            self.current_article_url = article_url

        except requests.RequestException as e:
            error_message = f"Error fetching html from page {article_url}: {e}"
            logger.error(error_message)
            return False

        return True

    @abstractmethod
    def _get_image_link(self) -> Optional[str]:
        """
        Use self.current_html_code and self.current_article_url to get the link of the main image of the url

        Returns: Optional[str] -> url of the main image if any
        """
        pass

    def extract(self, article_url: str) -> Optional[str]:
        """
        Orchestrates the image URL extraction
        Args:
            article_url: str -> URL that is required to get its html code

        Returns: Optional[str] -> URL of the main image of the url
        """

        if self._fetch_html_code(article_url):
            return self._get_image_link()

        return None


class MITImageExtractor(BaseImageExtractor):
    # Once defined _feed_url, automatically gets _base_feed_url due to the definition
    # in BaseImageExtractor
    _feed_url: str = news_config.MIT_NEWS_FEED_URL

    # property decorator allows to access a method as if it was an attribute
    # also creates a read-only attribute
    @property
    def feed_url(self):
        return self._feed_url

    @property
    def base_feed_url(self):
        return self._base_feed_url

    def _get_image_link(self) -> Optional[str]:
        """
        Get the main image from the MIT site

        Return:
            Optional[str] -> Link to the main image
        """
        try:
            image_tag = self.current_html_code.find(
                "div", class_="news-article--media--image--file"
            ).find("img")
            image_src = image_tag.get("data-src")
            return self.base_feed_url + image_src

        except Exception as e:
            logger.warning(
                f"Structure to get the image of the url {self.current_article_url} was't found: {e}"
            )
            return None


class AINEWSImageExtractor(BaseImageExtractor):
    # Private class attributes
    _feed_url: str = news_config.AI_NEWS_FEED_URL

    # property decorator allows to access a method as if it was an attribute
    # also creates a read-only attribute
    @property
    def feed_url(self):
        return self._feed_url

    @property
    def base_feed_url(self):
        return self._base_feed_url

    def _get_image_link(self) -> Optional[str]:
        """
        Get the main image from the AINEWS article site

        Return:
            Optional[str] -> Link to the main image
        """
        try:
            all_containers = self.current_html_code.select(
                ".elementor-widget-container"
            )
            containers_with_images = [c for c in all_containers if c.find("img")]
            image_url = [
                container.find("img").get("src")
                for container in containers_with_images
                if container.find("img").get("width") == "800"
            ][0]

            return image_url

        except Exception as e:
            logger.warning(
                f"Structure to get the image of the url {self.current_article_url} was't found: {e}"
            )

            return None
