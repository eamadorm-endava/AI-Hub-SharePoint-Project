from pydantic import BaseModel, Field
from typing import Annotated

from news_extraction_pipeline.config import AINewsConfig

news_config = AINewsConfig()


class ExtractionPipelineResponse(BaseModel):
    total_articles: Annotated[
        int,
        Field(
            description="Total number of articles extracted",
            ge=0,
        ),
    ]
    data: Annotated[
        list[dict],
        Field(
            description="list of dictionaries, each dictionary is an extrated article"
        ),
    ]
