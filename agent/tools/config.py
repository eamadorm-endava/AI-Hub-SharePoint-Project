from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, PrivateAttr
from typing import Annotated
from loguru import logger

from agent.config import GCPConfig


class TTSToolConfig(BaseSettings, validate_assignment=True):
    """
    Configuration class for Text-to-Speech (TTS) tool.
    """

    # Private attributes cannot be added in Annotated
    _CLOUD_PROVIDER: GCPConfig = PrivateAttr(default=GCPConfig())
    _GEMINI_API_KEY: SecretStr = PrivateAttr(default=SecretStr("dummy-api-key"))

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
            default="Emma",
            description="Name of the second custom person for TTS.",
        ),
    ]

    def __init__(self):
        super().__init__()
        self.load_gemini_api_key()

    def load_gemini_api_key(self):
        try:
            self._GEMINI_API_KEY = self._CLOUD_PROVIDER.get_secret(
                secret_id=self._CLOUD_PROVIDER.GEMINI_API_KEY_NAME,
                version_id=self._CLOUD_PROVIDER.GEMINI_API_KEY_VERSION,
            )
        except Exception as e:
            logger.error(f"Error loading Gemini API key: {e}")

    # Creating a read-only property for GEMINI_API_KEY
    @property
    def GEMINI_API_KEY(self) -> SecretStr:
        return self._GEMINI_API_KEY

    # To force to read .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
