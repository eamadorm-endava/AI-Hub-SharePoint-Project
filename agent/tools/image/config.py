from pydantic import Field
from typing import Annotated
from agent.tools.config import GCPToolConfig


class ImaGenToolConfig(GCPToolConfig, validate_assignment=True):
    """
    Configuration class for Image Generation tool.
    Inherits API key loading logic from GCPToolConfig.
    """

    MODEL_NAME: Annotated[
        str,
        Field(
            default="imagen-4.0-generate-001",
            description="Name of the model that will generate the images",
        ),
    ]
    MODEL_TEMPERATURE: Annotated[
        float,
        Field(
            default=0.8,
            description="Controls randomness in model output: lower values make responses more focused, higher values more creative.",
            ge=0,
            le=1,
        ),
    ]
    GCS_PATH: Annotated[
        str,
        Field(
            default="images/",
            description="Path inside the GCS Bucket where the images generated will be stored",
        ),
    ]
    DEFAULT_GENERATED_IMAGES: Annotated[
        int,
        Field(
            default=1,
            description="Number of images to generate each time the tool is executed",
            gt=0,
            lt=5,
        ),
    ]
    CONTENT_TYPE: Annotated[
        str,
        Field(
            default="image/png",
            description="Type of data that is stored in GCP",
        ),
    ]

    @property
    def tool_name(self) -> str:
        return "image_generation"
