from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr, PrivateAttr
from typing import Annotated
from loguru import logger
from utils.gcp.secret_manager import get_secret


class GCPConfig(BaseSettings, validate_assignment=True):
    """
    Class that holds configuration values for GCP services. Allowing to, in any future, change the
    cloud provider or the way to access the secrets.
    """

    PROJECT_ID: Annotated[
        str,
        Field(
            default="dummy-gcp-project-id",
            description="GCP Project ID",
        ),
    ]
    REGION: Annotated[
        str,
        Field(
            default="dummy-gcp-region",
            description="GCP Region where most of the services will be deployed",
        ),
    ]
    GEMINI_API_KEY_NAME: Annotated[
        str,
        Field(
            default="dummy-gemini-secret-name",
            description="Name of the secret in Secret Manager that contains the Gemini API key.",
        ),
    ]
    GEMINI_API_KEY_VERSION: Annotated[
        int,
        Field(
            default=1,
            description="Version of the secret in Secret Manager that contains the Gemini API key.",
        ),
    ]
    BUCKET_NAME: Annotated[
        str,
        Field(
            default="dummy-gcp-bucket-name",
            description="GCP Bucket name for storing agent related data.",
        ),
    ]
    SYSTEM_PROMPT_PATH: Annotated[
        str,
        Field(
            default="system_prompts/system_prompt_third_proposal.txt",
            description="GCS path to the system prompt file.",
        ),
    ]

    def get_secret(self, secret_id: str, version_id: int) -> SecretStr:
        """
        Get secrets from the secret manager.

        Args:
            secret_id (str): The ID of the secret to retrieve.
            version_id (int): The version of the secret to retrieve.

        Returns:
            SecretStr: The secret value.
        """
        return get_secret(
            secret_id=secret_id,
            version_id=version_id,
            project_id=self.PROJECT_ID,
        )

    # To force to read .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


class AgentConfig(BaseSettings, validate_assignment=True):
    """
    Class that holds configuration values for the agent, it requires to assign
    parameters after initialization.
    """

    # Private attributes cannot be added in Annotated
    _CLOUD_PROVIDER: GCPConfig = PrivateAttr(default=GCPConfig())
    _GEMINI_API_KEY: SecretStr = PrivateAttr(default=SecretStr("dummy-api-key"))

    # Public attributes
    GEMINI_MODEL_NAME: Annotated[
        str,
        Field(
            default="gemini-2.5-pro",
            description="Name of the Gemini model to use.",
        ),
    ]
    MODEL_TEMPERATURE: Annotated[
        float,
        Field(
            default=0.5,
            description="Controls randomness in model output: lower values make responses more focused, higher values more creative.",
            ge=0,
            le=1,
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
        extra = "allow"
