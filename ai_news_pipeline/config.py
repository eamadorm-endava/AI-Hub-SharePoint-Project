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
    LOCAL_FILE_PATH: Annotated[
        str,
        Field(
            default="path-to-local-storage.xlsx",
            description="The local file path to store the AI news Excel file.",
            pattern=r".*\.xlsx$",
        ),
    ]
    SEARCH_KEYWORDS: Annotated[
        list[str],
        Field(
            default=[
                " AI ", "AI ", "AI ", "A.I.", " AI-", "AI-", "Artificial Intelligence", "Machine Learning", "Deep Learning", 
                "Neural Networks", "NLP", "Computer Vision", "Data Science", "Gemini", 
                "Bard", "ChatGPT", "GPT-4", "DALL-E", "MidJourney", "Stable Diffusion", 
                "Claude", "LLaMA", "Whisper"
            ],
            description="List of keywords to filter AI news articles.",
        ),
    ]
    DAYS_BACK: Annotated[
        int,
        Field(
            default=2,
            description="Number of days back to filter news articles.",
            ge=1,
        ),
    ]
    DATE_COLUMN: Annotated[
        str,
        Field(
            default="publish_date",
            description="The name of the date column in the news DataFrame.",
            pattern=r"^\w+$",
        ),
    ]
