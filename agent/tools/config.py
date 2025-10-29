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


class VideoGenToolConfig(GCPToolConfig, validate_assignment=True):
    """
    Parameters of the Model that generates the videos.

    Check the documentation here: https://ai.google.dev/gemini-api/docs/video?example=dialogue
    """

    VIDEO_MODEL: Annotated[
        str,
        Field(
            default="veo-2.0-generate-001",
            description="Gemini Model that is used to generate videos",
        ),
    ]
    GCS_PATH: Annotated[
        str,
        Field(
            default="videos/",
            description="Path where the videos will be stored",
        ),
    ]
    GCS_CONTENT_TYPE: Annotated[
        str,
        Field(
            default="video/mp4",
            description="Content type stored in GCS",
        ),
    ]

    @property
    def tool_name(self) -> str:
        return "video_generation"
