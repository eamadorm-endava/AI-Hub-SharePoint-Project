from pydantic import BaseModel, Field
from typing import Annotated


class ImagePromptInfo(BaseModel):
    prompt: Annotated[
        str,
        Field(description="Prompt describing the image to be generated"),
    ]
    image_name: Annotated[
        str,
        Field(description="Name of the image. (e.g. spider_in_the_rain)"),
    ]
