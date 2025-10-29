from pydantic import BaseModel, Field, HttpUrl
from typing import Annotated, Optional, Literal
from agent.tools.config import TTSToolConfig

tts_config = TTSToolConfig()


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
    gcs_path: Annotated[
        str,
        Field(
            default=tts_config.TTS_MODEL,
            description="Path where the audio will be stored in gcs. (e.g. audio/)",
            pattern=r"^(\w/)*\w+$",
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
    full_gcs_path: Annotated[
        str,
        Field(
            description="GCS Path where the audio was stored (e.g. gcs/path/to/audio.wav).",
            pattern=r"^[\w/]+.wav$",
        ),
    ]
