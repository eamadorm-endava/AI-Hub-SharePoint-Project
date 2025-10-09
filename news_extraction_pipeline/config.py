from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


class AINewsConfig(BaseSettings):
    MIT_NEWS_FEED_URL: Annotated[
        str,
        Field(
            default="https://news.mit.edu/rss/feed",
            description="The RSS feed URL for the MIT page",
        ),
    ]
    AI_NEWS_FEED_URL: Annotated[
        str,
        Field(
            default="https://www.artificialintelligence-news.com/artificial-intelligence-news/feed/",
            description="The RSS feed URL for AI news.",
        ),
    ]
    BASE_URL_PATTERN: Annotated[
        str,
        Field(
            default=r"https://[\w\.-]+/",
            description="Pattern to get the base url",
        ),
    ]
    DATE_COLUMN: Annotated[
        str,
        Field(
            default="publish_date",
            description="Name of the DataFrame column to filter by date",
        ),
    ]
    DATE_STRING_FORMAT: Annotated[
        str,
        Field(
            default=r"%Y-%m-%dT%H:%M:%SZ",
            description="String format representing the datetime value",
        ),
    ]
    COLUMN_TO_FILTER_BY_KW: Annotated[
        str,
        Field(
            default="title",
            description="Name of the column that will be filtered by keywords",
        ),
    ]

    # To force to read .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
