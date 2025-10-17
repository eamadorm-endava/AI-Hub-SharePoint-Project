from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Annotated
from utils.gcp.secret_manager import get_secret


class AgentConfig(BaseSettings, validate_assignment=True):
    """
    Class that holds configuration values for the agent, it requires to assign
    parameters after initialization.
    """

    __GEMINI_API_KEY: Annotated[
        SecretStr,
        Field(
            default="dummy_key",
            description="Gemini API key.",
            min_length=1,
        ),
    ]
    GEMINI_MODEL_NAME: Annotated[
        str,
        Field(
            default="gemini-1.5-pro",
            description="Name of the Gemini model to use.",
        ),
    ]

    def __init__(self):
        super().__init__()
        self.__load_gemini_api_key()

    def __load_gemini_api_key(self) -> None:
        """
        Get secrets from the secret manager.
        """
        gcp_config = GCPConfig()
        self.__GEMINI_API_KEY = get_secret(
            secret_id=gcp_config.GEMINI_API_KEY_NAME,
            version_id=gcp_config.GEMINI_API_KEY_VERSION,
            project_id=gcp_config.PROJECT_ID,
        )

    # Creating a read-only property for GEMINI_API_KEY
    @property
    def GEMINI_API_KEY(self) -> SecretStr:
        return self.__GEMINI_API_KEY

    # To force to read .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


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

    # To force to read .env file
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
