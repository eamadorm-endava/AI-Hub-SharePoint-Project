from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from typing import Annotated


class AgentConfig(BaseSettings, validate_assignment=True):
    """
    Class that holds configuration values for the agent, it requires to assign
    parameters after initialization.
    """

    PROMPT_TEMPLATE_PATH: str = "prompts/page_generator.txt"
    OPENAI_SECRET_NAME: str = "OPENAI-API-KEY"
    OPENAI_KEY: SecretStr = ""


class AzureConfig(BaseSettings):
    """
    Class that holds configuration values for Azure services. Allowing to, in any future, change the
    cloud provider or the way to access the secrets.
    """

    KEY_VAULT_URL: Annotated[
        str,
        Field(
            default="https://ai-hub-key-vault-endava.vault.azure.net/",
            description="URL to a key-vault on Azure",
            pattern="^https://[A-Za-z-]+.vault.azure.net/",
        ),
    ]
