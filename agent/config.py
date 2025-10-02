from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Annotated
from utils.azure.key_vaults import get_secret


class AgentConfig(BaseSettings, validate_assignment=True):
    """
    Class that holds configuration values for the agent, it requires to assign
    parameters after initialization.
    """

    PROMPT_TEMPLATE_PATH: Annotated[
        str,
        Field(default="prompts/page_generator.txt"),
    ]
    OPENAI_KEY: Annotated[
        SecretStr,
        Field(
            default="dummy_key",
            description="OpenAI API key.",
            min_length=1,
        ),
    ]

    def load_secrets(self) -> None:
        """
        Get secrets from key-vault.
        """
        azure_config = AzureConfig()
        secret_name = azure_config.OPENAI_SECRET_NAME
        vault_url = azure_config.KEY_VAULT_URL
        secret_value = get_secret(vault_url, secret_name)
        self.OPENAI_KEY = secret_value


class AzureConfig(BaseSettings, validate_assignment=True):
    """
    Class that holds configuration values for Azure services. Allowing to, in any future, change the
    cloud provider or the way to access the secrets.
    """

    KEY_VAULT_URL: Annotated[
        str,
        Field(
            default="https://dummy-key-vault.vault.azure.net/",
            description="URL to a key-vault on Azure",
            pattern="^https://[A-Za-z-]+.vault.azure.net/",
        ),
    ]
    AIHUB_APP_CLIENT_ID: Annotated[
        str,
        Field(
            default="dummy-app-client-id",
            description="Client ID of the AI-Hub application registered in Microsoft Entra",
        ),
    ]
    AIHUB_APP_TENANT_ID: Annotated[
        str,
        Field(
            default="dummy-app-tenant-id",
            description="Client ID of the AI-Hub application registered in Microsoft Entra",
        ),
    ]
    AIHUB_APP_CLIENT_SECRET_NAME: Annotated[
        str,
        Field(
            default="dummy-app-client-secret-name",
            description="Name of the secret in Key Vault that contains the client secret for Microsoft Graph API.",
        ),
    ]
    AIHUB_APP_CLIENT_SECRET_VALUE: Annotated[
        SecretStr,
        Field(
            default="dummy-app-client-secret-value",
            description="Client secret for the AI-Hub application registered in Microsoft Entra",
        ),
    ]
    OPENAI_SECRET_NAME: Annotated[
        str,
        Field(
            default="dummy-openai-secret-name",
            description="Name of the secret in Key Vault that contains the OpenAI API key.",
        ),
    ]

    def load_secrets(self) -> None:
        """
        Get Azure secrets from key-vault.
        """
        self.AIHUB_APP_CLIENT_SECRET_VALUE = get_secret(
            vault_url=self.KEY_VAULT_URL, secret_name=self.AIHUB_APP_CLIENT_SECRET_NAME
        )
