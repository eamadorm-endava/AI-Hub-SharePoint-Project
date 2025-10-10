from pydantic import BaseModel, Field, field_validator
from typing import Annotated


class PipelineArgs(BaseModel):
    case_sen_search_kw: Annotated[
        list[str],
        Field(
            default=[
                " AI ",
                "AI ",
                "AI ",
                "A.I.",
                " AI-",
                "AI-",
            ],  # In case this field is not included
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
    max_days_old: Annotated[
        int,
        Field(
            default=2,
            description="Maximum number of days since publication.",
            ge=1,
        ),
    ]

    @field_validator("case_sen_search_kw", "case_insen_search_kw", mode="after")
    @classmethod
    def no_empty_kw(cls, kw_list: list[str]) -> list[str]:
        cleaned = [kw.strip() for kw in kw_list if kw.strip()]

        if not cleaned:
            raise ValueError(
                "Both, case_sen_search_kw and case_insen_search_kw must "
                "contain at least one non-empty string value"
            )

        return cleaned
