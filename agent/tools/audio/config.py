from pydantic import Field
from typing import Annotated
from agent.tools.config import GCPToolConfig


class TTSToolConfig(GCPToolConfig):
    """
    Configuration class for Text-to-Speech (TTS) tool.
    Inherits API key loading logic from GCPToolConfig.
    """

    TTS_MODEL: Annotated[
        str,
        Field(
            default="gemini-2.5-flash-preview-tts",
            description="The TTS model to be used for generating speech.",
        ),
    ]
    # For voice name, check https://cloud.google.com/text-to-speech/docs/gemini-tts
    FIRST_SPEAKER_VOICE: Annotated[
        str,
        Field(
            default="Leda",
            description="Name of the first pre-built voice for TTS.",
        ),
    ]
    SECOND_SPEAKER_VOICE: Annotated[
        str,
        Field(
            default="Umbriel",
            description="Name of the second pre-built voice for TTS.",
        ),
    ]
    FIRST_SPEAKER_NAME: Annotated[
        str,
        Field(
            default="Wendy",
            description="Name of the first custom person for TTS.",
        ),
    ]
    SECOND_SPEAKER_NAME: Annotated[
        str,
        Field(
            default="Matt",
            description="Name of the second custom person for TTS.",
        ),
    ]
    GCS_PATH: Annotated[
        str,
        Field(
            default="audios/",
            description="Path inside the GCS Bucket where the audio generated will be stored",
        ),
    ]
    PUBLIC_AUDIO: Annotated[
        bool,
        Field(
            default=True,
            description="True if the blob will be public, otherwise False",
        ),
    ]

    @property
    def tool_name(self) -> str:
        return "text_to_speech"
