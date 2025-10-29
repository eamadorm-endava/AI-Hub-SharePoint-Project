import feedparser
import pandas as pd
from loguru import logger
from typing import Type, Optional

from news_extraction_pipeline.extractor_selectors.extractor_selector import (
    ImageExtractorSelector,
)
from news_extraction_pipeline.extractors.image_url.image_url_extractors import (
    BaseImageExtractor,
)


class NewsExtractor:
    __img_extr_selector: ImageExtractorSelector = ImageExtractorSelector()

    def __init__(self):
        """
        Initializes a NewsExtractor instance.
        """
        # Private attributes, which cannot be directly accessed from the outside
        self.__current_feed_url: Optional[str] = None
        self.__previous_feed_url: Optional[str] = None
        self.__img_extractor: Optional[Type[BaseImageExtractor]] = None
        self.__current_data: Optional[pd.DataFrame] = None

    # @property -> to create a read-only attribute without exposing the real one.
    # Won't be allowed to set the attribute:
    #   extractor.previous_feed_url = "https://..." (raise AttributeError)
    @property
    def current_data(self):
        return self.__current_data

    @property
    def previous_feed_url(self):
        return self.__previous_feed_url

    # To create an attribute with a specific setter logic
    # In this case, everytime the attribute 'current_feed_url' is rewritten
    # the current_feed_url function will be executed
    @property
    def current_feed_url(self):
        return self.__current_feed_url

    @current_feed_url.setter
    def current_feed_url(self, feed_url: str) -> None:
        """
        Set feed url and automatically select an ImageExtractor class

        Args:
            feed_url: str -> RSS-compatible URL to retrieve news articles from.

        Returns:
            None
        """
        if not isinstance(feed_url, str):
            logger.error("feed_url must be a string")
            return

        if not feed_url.startswith("https://"):
            logger.error("feed_url must start with 'https://'")

        # Setting the feed_url and its ImageExtractor class
        logger.info(f"Setting current feed url to {feed_url}")
        self.__previous_feed_url = self.__current_feed_url
        self.__current_feed_url = feed_url
        self.__img_extractor = self.__img_extr_selector.get_extractor(
            self.__current_feed_url
        )

    # To allow set the attribute 'current_feed_url' in two different ways:
    #       - extractor.current_feed_url = "https://..."
    #       - extractor.set_current_feed_url("https://...")
    # Both ways will also update 'previous_feed_url', which is a read-only attribute
    def set_current_feed_url(self, feed_url: str) -> None:
        self.current_feed_url = feed_url

    def articles_extracted(self) -> bool:
        """
        Verifies if the articles previously extracted comes from the same proposed_feed_url, if so,
        returns True, otherwise False

        Returns:
            bool -> True if the articles from the feed_url has already been extracted
        """

        # In case self.__current_data has not been instanciated yet or the feed_url is different
        return (
            isinstance(self.__current_data, pd.DataFrame)
            and self.__previous_feed_url == self.__current_feed_url
        )

    def get_articles(self) -> Optional[pd.DataFrame]:
        """
        Retrieves AI-related news data in its raw format from the feed_url. The data obtained per news is:
            - title
            - news_link
            - image_link
            - publish_date

        The data obtained is stored in self.__current_data

        Returns:
            Optional[pd.DataFrame] -> The data obtained
        """
        if self.articles_extracted():
            logger.info(
                f"Articles from feed url {self.__previous_feed_url} already extracted"
            )
            return self.__current_data

        try:
            feed = feedparser.parse(self.__current_feed_url)

        except Exception as e:
            logger.error(
                f"Articles from {self.__current_feed_url} could not be extracted: {e}"
            )

        extracted_articles = [
            {
                "title": entry.title.replace("'", ""),  # To avoid issues with strings
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

            # publish_date might have different timezones, so I pass them all to the
            # UTC - 00:00 timezone
            articles.publish_date = pd.to_datetime(articles.publish_date).dt.tz_convert(
                "UTC"
            )

            self.__current_data = articles
            self.__previous_feed_url = self.__current_feed_url

        else:
            logger.error(
                f"No articles extracted from {self.__current_feed_url} "
                " Make sure the url is RSS-compatible"
            )
            # Restores the attribute current_data to avoid mix articles
            # of different feed urls
            self.__current_data = None

        return self.__current_data
