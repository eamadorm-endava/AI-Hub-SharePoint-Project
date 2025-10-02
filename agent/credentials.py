from functools import lru_cache
from agent.config import AgentConfig, AzureConfig
from agent.utils.azure.key_vaults import get_secret

agent_config = AgentConfig()
azure_config = AzureConfig()


@lru_cache
def get_agent_config() -> AgentConfig:
    """
    Get the agent configuration, fetching the OpenAI secret from Azure Key Vault if not already set.
    @lru_cache is used to cache the result for future calls. So the returned class instance is a singleton.

    Returns:
        AgentConfig: The agent configuration
    """
    secret_name = agent_config.OPENAI_SECRET_NAME
    vault_url = azure_config.KEY_VAULT_URL
    secret_value = get_secret(vault_url, secret_name)

    return AgentConfig(OPENAI_KEY=secret_value)
