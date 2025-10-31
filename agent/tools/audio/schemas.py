from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Annotated, Optional, Literal


# Commond Fields
GCS_AUDIO_PATH = Annotated[
    str,
    Field(
        description="GCS Path where the audio was stored (e.g. gcs/path/to/audio.wav).",
        pattern=r"^[\w/]+.wav$",
    ),
]


class TTSRequest(BaseModel, validate_assignment=True):
    title: Annotated[
        str,
        Field(
            description="Title of the audio generated. (e.g. my_audio)",
            pattern=r"^[\w]+$",
        ),
    ]
    text: Annotated[
        str,
        Field(
            description="Text to be converted into speech.",
            min_length=1,
        ),
    ]
    mode: Annotated[
        Literal["single", "multi"],
        Field(
            description="Define if the speech is single or multi speaker",
        ),
    ]


class TTSResponse(BaseModel, validate_assignment=True):
    title: Annotated[
        str,
        Field(
            description="Title of the audio generated. (e.g. my_audio)",
            pattern=r"^[\w]+$",
        ),
    ]
    public_url: Annotated[
        Optional[HttpUrl],
        Field(
            default=None,
            description="URL where the generated audio can be listened and downloaded.",
        ),
    ]
    full_gcs_path: GCS_AUDIO_PATH


class AudioDurationRequest(BaseModel, validate_assignment=True):
    name: GCS_AUDIO_PATH


class AudioDurationResponse(AudioDurationRequest):
    model_config = ConfigDict(validate_assignment=True)

    duration_seconds: Annotated[
        float,
        Field(
            description="Total duration of the audio in seconds",
            ge=0,
        ),
    ]
