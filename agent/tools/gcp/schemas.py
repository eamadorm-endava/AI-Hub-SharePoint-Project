from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Annotated, Literal, Optional
from datetime import datetime


class Blob(BaseModel, validate_assignment=True):
    name: Annotated[
        str,
        Field(
            description="Generic blob name with extension (e.g. folder/file.txt)",
            pattern=r"^([\w-]+/)*[\w-]+\.[A-Za-z0-9]+$",
        ),
    ]
    content_type: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Content type of the bucket. (e.g. text/plain)",
        ),
    ]
    public_url: Annotated[
        Optional[HttpUrl],
        Field(
            default=None,
            description="Public URL where the blob can be access to or downloaded",
        ),
    ]
    storage_class: Annotated[
        Optional[Literal["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"]],
        Field(
            default=None,
            description="Type of storage class",
        ),
    ]
    size_bytes: Annotated[
        Optional[float],
        Field(
            default=None,
            description="The size of the object, in bytes",
            gt=0,
        ),
    ]
    created_at: Annotated[
        Optional[datetime],
        Field(
            default=None,
            description="Timestamp when the blob was created",
        ),
    ]
    updated_at: Annotated[
        Optional[datetime],
        Field(default=None, description="Timestamp when the blob was updated"),
    ]


class TextBlob(Blob):
    model_config = ConfigDict(validate_assignment=True)

    name: Annotated[
        str,
        Field(
            description="Name of the blob (e.g. gcs_path/file_name.txt)",
            pattern=r"^(\w+/)*\w+\.txt$",
        ),
    ]
    text: Annotated[
        str,
        Field(
            default=None,  # In case this field is not explicitly set
            description="Text to be stored into GCS",
            min_length=1,
        ),
    ]
