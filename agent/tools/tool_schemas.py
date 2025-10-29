from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Optional, Literal


class ImaGenRequest(BaseModel):
    prompt: Annotated[
        str,
        Field(description="Prompt describing the image to be generated"),
    ]
    image_name: Annotated[
        str,
        Field(description="Name of the image. (e.g. spider_in_the_rain)"),
    ]


class Image(ImaGenRequest):
    gcs_path: Annotated[
        str,
        Field(
            default=None,
            description="Path in Google Cloud Storage where the image will be stored. (e.g.: my/gcs/folder/image_name.png)",
            pattern=r"[\w]+/*\.png",
        ),
    ]
    public_url: Annotated[
        HttpUrl,
        Field(
            default=None,  # In case the parameter is not set while creating the object instance
            description="Public URL to access the image generated",
        ),
    ]
    image_bytes: Annotated[
        Optional[bytes],
        Field(
            default=None,
            description="Bytes of the image generated",
        ),
    ]

    class Config:
        validate_assignment = True


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
