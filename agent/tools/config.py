from abc import ABC, abstractmethod
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, PrivateAttr
from typing import Annotated
from loguru import logger

from agent.config import GCPConfig


class GCPToolConfig(ABC, BaseSettings):
    """
    Abstract base class for tool configurations that require a Gemini API key.
    It handles the loading of the API key from the secret manager.
    """

    _CLOUD_PROVIDER: GCPConfig = PrivateAttr(default=GCPConfig())
    _GEMINI_API_KEY: SecretStr = PrivateAttr(default=SecretStr("dummy-api-key"))

    def __init__(self):
        super().__init__()
        self.load_gemini_api_key()

    def load_gemini_api_key(self):
        """
        Loads the Gemini API key from the configured secret manager.
        """
        try:
            self._GEMINI_API_KEY = self._CLOUD_PROVIDER.get_secret(
                secret_id=self._CLOUD_PROVIDER.GEMINI_API_KEY_NAME,
                version_id=self._CLOUD_PROVIDER.GEMINI_API_KEY_VERSION,
            )
            logger.debug(f"API Key loaded successfully for {self.tool_name}.")
        except Exception as e:
            logger.error(f"Error loading Gemini API key for {self.tool_name}: {e}")

    @property
    def GEMINI_API_KEY(self) -> SecretStr:
        """Read-only property to access the loaded Gemini API key."""
        return self._GEMINI_API_KEY

    @property
    @abstractmethod
    def tool_name(self):
        pass

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


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
            default="Emma",
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

    @property
    def tool_name(self) -> str:
        return "text_to_speech"


class ImaGenToolConfig(GCPToolConfig, validate_assignment=True):
    """
    Configuration class for Image Generation tool.
    Inherits API key loading logic from GCPToolConfig.
    """

    MODEL_NAME: Annotated[
        str,
        Field(
            default="gemini-2.5-flash-image",
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

    @property
    def tool_name(self) -> str:
        return "image_generation"
