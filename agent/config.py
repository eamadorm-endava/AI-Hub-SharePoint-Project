from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Annotated


class AgentConfig(BaseSettings):
    PROMPT_TEMPLATE_PATH: str = "prompts/page_generator.txt"
    OPENAI_SECRET_NAME: str = "OPENAI-API-KEY"


class AzureConfig(BaseSettings):
    KEY_VAULT_URL: Annotated[
        str,
        Field(
            default="https://ai-hub-key-vault-endava.vault.azure.net/",
            description="URL to a key-vault on Azure",
            pattern="^https://[A-Za-z-]+.vault.azure.net/",
        ),
    ]
