from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


class AINewsSettings(BaseSettings):
    NEWS_URL: Annotated[
        str,
        Field(
            default="https://www.artificialintelligence-news.com/artificial-intelligence-news/feed/",
            description="The RSS feed URL for AI news.",
            pattern=r"^https?://.*/feed/",
        ),
    ]
