from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Annotated
from ..config import GCPToolConfig


class VideoGenToolConfig(GCPToolConfig, validate_assignment=True):
    """
    Parameters of the Model that generates the videos.

    Check the documentation here: https://ai.google.dev/gemini-api/docs/video?example=dialogue
    """

    VIDEO_MODEL: Annotated[
        str,
        Field(
            default="veo-2.0-generate-001",
            description="Gemini Model that is used to generate videos",
        ),
    ]
    GCS_PATH: Annotated[
        str,
        Field(
            default="videos/",
            description="Path where the videos will be stored",
        ),
    ]
    GCS_CONTENT_TYPE: Annotated[
        str,
        Field(
            default="video/mp4",
            description="Content type stored in GCS",
        ),
    ]

    @property
    def tool_name(self) -> str:
        return "video_generation"


class PodcastVideoConfig(BaseSettings):
    COVER_IMAGE: Annotated[
        str,
        Field(
            default="images/ai_conversations_cover.png",
            pattern=r"^(\w+/)*\w+\.png$",
        ),
    ]
    TEMP_LOCAL_STORAGE: Annotated[
        str,
        Field(
            default="./temp/",
            description="Folder where files could be temporally stored",
        ),
    ]
    GCS_PATH: Annotated[
        str,
        Field(
            default="videos/",
            description="Path inside the GCS Bucket where the audio generated will be stored",
        ),
    ]
    IS_PUBLIC: Annotated[
        bool,
        Field(
            default=True,
            description="True if the blob will be public, otherwise False",
        ),
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
