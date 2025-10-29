from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Optional


class ImaGenRequest(BaseModel):
    prompt: Annotated[
        str,
        Field(
            description="Prompt describing the image to be generated",
            min_length=1,
        ),
    ]
    image_name: Annotated[
        str,
        Field(
            description="Name of the image. (e.g. spider_in_the_rain)",
            min_length=1,
            pattern=r"^[\w]+$",
        ),
    ]


class Image(ImaGenRequest):
    gcs_path: Annotated[
        str,
        Field(
            default=None,
            description="Path in Google Cloud Storage where the image will be stored. (e.g.: my/gcs/folder/image_name.png)",
            pattern=r"^(\w+/)*\w+\.png$",
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
