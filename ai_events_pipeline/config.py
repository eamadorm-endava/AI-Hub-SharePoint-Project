from pydantic_settings import BaseSettings


class DataSources(BaseSettings):
    TOP_AI_CONFERENCES: str = "https://www.unite.ai/conferences/"
    INSIDR_CONFERENCES: str = (
        "https://www.insidr.ai/ai-community/ai-guides/ai-conferences/"
    )
