from pydantic import Field
from typing import Annotated
from ..config import GCPToolConfig


class GCSToolConfig(GCPToolConfig):
    CONTENT_TYPE: Annotated[
        str,
        Field(
            default="text/plan",
            description="Type of content that can be uploaded to GCS",
            pattern=r"\w+/\w+",
        ),
    ]

    @property
    def tool_name(self):
        return "cloud_storage"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
