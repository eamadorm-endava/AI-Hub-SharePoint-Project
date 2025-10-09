from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


# Common fields
case_insen_search_kw = Annotated[
    list[str],
    Field(
        default=[
            "Artificial Intelligence",
            "Machine Learning",
            "Deep Learning",
            "Neural Networks",
            "NLP",
            "Computer Vision",
            "Data Science",
            "Gemini",
            "Bard",
            "ChatGPT",
            "GPT-4",
            "DALL-E",
            "MidJourney",
            "Stable Diffusion",
            "Claude",
            "Whisper",
        ],
        description="List of keywords to filter AI news articles. This will be matched no matter the case",
    ),
]
case_sen_search_kw = Annotated[
    list[str],
    Field(
        default=[" AI ", "AI ", "AI ", "A.I.", " AI-", "AI-"],
        description="List of keywords to filter AI News articles by. This will be an exact match",
    ),
]
max_days_old = Annotated[
    int,
    Field(
        default=2,
        description="Maximum number of days since publication.",
        ge=1,
    ),
]


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
    CASE_INSEN_SEARCH_KW: case_insen_search_kw
    CASE_SEN_SEARCH_KW: case_sen_search_kw
    MAX_DAYS_OLD: max_days_old

    # To force to read .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
