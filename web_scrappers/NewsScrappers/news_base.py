from web_scrappers.base import WebScrapper
from ai_news_pipeline.config import AINewsConfig
import re

news_config = AINewsConfig()


class NewsScrapper(WebScrapper):
    """
    Class that retrieves news from different urls
    """

    # private attribute, it is not accesible from outside the class
    # It is also a class attribute, meaning that all the instances of this class will have
    # the same value
    __base_url_pattern: str = news_config.BASE_URL_PATTERN

    def __init__(
        self,
        feed_url: str,
        case_sen_search_kw: list[str] = news_config.CASE_SEN_SEARCH_KW,
        case_insen_search_kw: list[str] = news_config.CASE_INSEN_SEARCH_KW,
    ):
        # Private attributes, cannot be directly accessed from outside the class
        self.__feed_url = feed_url
        self.__base_url = (
            re.search(self.__base_url_pattern, self.__feed_url).group().rstrip()
        )

        # Public attributes, can be directly accessed and modified from outsite the class
        self.case_sen_search_kw = case_sen_search_kw
        self.case_insen_search_kw = case_insen_search_kw

    @property
    def feed_url(self):
        return self.__feed_url

    @property
    def base_url(self):
        return self.__base_url
