from pydantic.functional_serializers import PlainSerializer
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Annotated, Optional


# Common Field Validators
STRING_NORMALIZER = BeforeValidator(
    lambda text: str(text).strip() if text is not None else None
)

SERIALIZED_DATETIME_FORMAT = r"%Y-%m-%d %H:%M:%S"


class NewsMetadata(BaseModel, validate_assignment=True):
    """
    This class will receive the news metadata obtained
    """

    news_id: Annotated[
        str,  # If this field is included, it must be a string
        Field(
            default=None,  # In case this field is not included
            description="ID of the news. It is obtained after adding it to a database",
        ),
    ]
    title: Annotated[
        str,
        Field(description="Title of the extracted news", min_length=1),
        STRING_NORMALIZER,
    ]
    published_at: Annotated[
        datetime,
        Field(description="Datetime when the news was published"),
        PlainSerializer(  # Tells pydantic when serializing (converting to a dict or a json string), use the function
            lambda dt: dt.strftime(SERIALIZED_DATETIME_FORMAT),
            when_used="always",
        ),
    ]
    extracted_at: Annotated[
        datetime,
        Field(
            default=None,  # In case this parameter is not explicitly set
            description="Datetime when the news was extracted from the web",
        ),
        PlainSerializer(  # Tells pydantic when serializing (converting to a dict or a json string), use the function
            lambda dt: dt.strftime(SERIALIZED_DATETIME_FORMAT),
            when_used="always",
        ),
    ]
    news_link: Annotated[
        str,
        Field(
            description="Link to the news",
            pattern="^https://.+",
        ),
        STRING_NORMALIZER,
    ]
    image_link: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Link to the main image of the news extracted",
            pattern="^https://.+",
        ),
        STRING_NORMALIZER,
    ]
