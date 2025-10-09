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
    FILE_PATH: Annotated[
        str,
        Field(
            default="path-to-local-storage.xlsx",
            description="The local file path to store the AI news Excel file.",
            pattern=r".*\.xlsx$",
        ),
    ]
    EXCEL_SHEET_NAME: Annotated[
        str,
        Field(
            default="AI-News",
            description="Name of the excel sheet where the data will be stored",
        ),
    ]
    EXCEL_TABLE_NAME: Annotated[
        str,
        Field(
            default="RecentAINews",
            description="Name of the excel table where the data will be stored",
        ),
    ]
    CASE_INSEN_SEARCH_KW: Annotated[
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
                "LLaMA",
                "Whisper",
            ],
            description="List of keywords to filter AI news articles. This will be matched no matter the case",
        ),
    ]
    CASE_SEN_SEARCH_KW: Annotated[
        list[str],
        Field(
            default=[" AI ", "AI ", "AI ", "A.I.", " AI-", "AI-"],
            description="List of keywords to filter AI News articles by. This will be an exact match",
        ),
    ]
    MAX_DAYS_OLD: Annotated[
        int,
        Field(
            default=2,
            description="Maximum number of days since publication.",
            ge=1,
        ),
    ]
    DATE_COLUMN: Annotated[
        str,
        Field(
            default="publish_date",
            description="Name of the DataFrame column to filter by date",
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
