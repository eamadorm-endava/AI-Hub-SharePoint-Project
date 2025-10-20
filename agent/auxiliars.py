from utils.gcp.gcs import get_file
from agent.config import GCPConfig

# Instantiate GCPConfig at the module level
gcp_config = GCPConfig()


def load_system_prompt():
    """
    Loads the system prompt file from Google Cloud Storage.

    This function retrieves the system prompt file using the configuration
    provided by the module-level 'gcp_config' instance.

    Returns:
        str: The content of the system prompt file, decoded as UTF-8.
    """
    bucket_name = gcp_config.BUCKET_NAME
    gcs_path = gcp_config.SYSTEM_PROMPT_PATH

    file_bytes = get_file(gcs_file_path=gcs_path, bucket_name=bucket_name)

    return file_bytes.decode("utf-8")
