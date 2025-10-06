from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


class AIEventsConfig(BaseSettings):
    TOP_AI_CONFERENCES: str = "https://www.unite.ai/conferences/"
    INSIDR_CONFERENCES: str = (
        "https://www.insidr.ai/ai-community/ai-guides/ai-conferences/"
    )
    MONTHS_IN_FUTURE: Annotated[
        int,
        Field(
            default=4,
            description="Max months in the future the AI-Events must start in",
            gt=0,
        ),
    ]
    AI_EVENTS_FILE_PATH: Annotated[
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
