from pydantic.functional_serializers import PlainSerializer
from pydantic import BaseModel, Field, BeforeValidator
from datetime import datetime
from typing import Annotated, Optional


# Common Field Validators
STRING_NORMALIZER = BeforeValidator(
    lambda text: str(text).strip() if text is not None else None
)


# Common fields
def datetime_field(mandatory: bool) -> Annotated[datetime, Field, PlainSerializer]:
    """
    If not mandatory, add a default value (None) if attribute is not defined when instanciated

    Args:
        mandatory: bool -> True if it must be set when the class is instanciated, otherwise False

    Returns:
        Annotated[datetime, Field, PlainSerializer] -> Annotated Datetime Field
    """
    field_args = {"description": "Datetime when a resource was created/added, etc"}
    if not mandatory:
        field_args["default"] = None

    return Annotated[
        datetime,
        Field(**field_args),
        PlainSerializer(  # Tells pydantic when serializing (converting to a dict or a json string), use the function
            lambda dt: dt.strftime(r"%Y-%m-%d %H:%M:%S"),
            when_used="always",
        ),
    ]


DATETIME_REQUIRED_FIELD = datetime_field(mandatory=True)
DATETIME_NOT_REQUIRED_FIELD = datetime_field(mandatory=False)


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
    published_at: DATETIME_REQUIRED_FIELD  # type: ignore
    extracted_at: DATETIME_NOT_REQUIRED_FIELD  # type: ignore
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
