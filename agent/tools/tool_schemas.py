from pydantic import BaseModel, Field
from typing import Annotated


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
        str,
        Field(
            default=None,  # In case the parameter is not set while creating the object instance
            description="Public URL to access the image generated",
        ),
    ]
    image_bytes: Annotated[
        bytes,
        Field(
            default=None,
            description="Bytes of the image generated",
        ),
    ]
