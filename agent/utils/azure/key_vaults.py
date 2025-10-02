from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from pydantic import SecretStr


credential = DefaultAzureCredential()


def get_secret(vault_url: str, secret_name: str) -> str:
    """
    Retrieve a secret from an Azure Key Vault. Code adapted from:
    https://learn.microsoft.com/en-us/python/api/overview/azure/keyvault-secrets-readme?view=azure-python#retrieve-a-secret

    Args:
        vault_url (str): The URL of the Azure Key Vault.
        secret_name (str): The name of the secret to retrieve.
    """
    secret_client = SecretClient(vault_url=vault_url, credential=credential)

    return SecretStr(secret_client.get_secret(secret_name).value)
