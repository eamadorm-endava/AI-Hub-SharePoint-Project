from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Annotated, Literal, Optional


class VideoGenRequest(BaseModel, validate_assignment=True):
    """
    Parameters of the Model that generates the video.

    Check the documentation here: https://ai.google.dev/gemini-api/docs/video?example=dialogue
    """

    title: Annotated[
        str,
        Field(
            description="Name of the title to be generated",
            min_length=1,
            pattern=r"^[\w/]+$",  # only upper and lower case, slashes, digits, and underscores
        ),
    ]
    prompt: Annotated[
        str,
        Field(
            description="Prompt describing the video",
            min_length=1,
        ),
    ]
    aspect_ratio: Annotated[
        Literal["9:16", "16:9"],
        Field(
            default="9:16",
            description="Aspect ratio of the video, only allowed 9:16 or 16:9",
        ),
    ]
    duration_seconds: Annotated[
        Literal[5, 6, 8],
        Field(
            default=8,
            description="Duration of the video generated in seconds. Only 5, 6, or 8 are allowed",
        ),
    ]

    class Config:
        validate_assignment = True


class VideoGenResponse(BaseModel, validate_assignment=True):
    video_url: Annotated[HttpUrl, Field(description="public URL to access the video")]

    class Config:
        validate_assignment = True


class PodcastVideoRequest(BaseModel, validate_assignment=True):
    gcs_audio_path: Annotated[
        str,
        Field(
            description="Name of the audio blob in cloud storage (e.g. gcs_path/file_name.wav)",
            pattern=r"^(\w+/)*\w+\.wav$",
        ),
    ]


class PodcastVideoResponse(PodcastVideoRequest):
    model_config = ConfigDict(validate_assignment=True)
    gcs_video_path: Annotated[
        str,
        Field(
            description="Name of the video podcast blob in cloud storage (e.g. gcs_path/file_name.mp4)",
            pattern=r"^(\w+/)*\w+\.mp4$",
        ),
    ]
    public_url: Annotated[
        Optional[HttpUrl],
        Field(
            description="Public URL where the podcast video can be access to",
        ),
    ]
