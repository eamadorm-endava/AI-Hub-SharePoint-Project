from pydantic import BaseModel, Field
from typing import Annotated


class PipelineArgs(BaseModel):
    case_sen_search_kw: Annotated[
        list[str],
        Field(
            default=[" AI ", "AI ", "AI ", "A.I.", " AI-", "AI-"],
            description="List of keywords to filter AI News articles by. This will be an exact match",
        ),
    ]
    case_insen_search_kw: Annotated[
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
    max_days_old = Annotated[
        int,
        Field(
            default=2,
            description="Maximum number of days since publication.",
            ge=1,
        ),
    ]
