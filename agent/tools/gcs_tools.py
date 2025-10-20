from loguru import logger
from utils.gcp.gcs import get_file, list_blobs
from agent.tools.config import TTSToolConfig


tts_config = TTSToolConfig()


def load_file_from_gcs(blob_name: str) -> bytes:
    """
    Load a file from GCS and return its bytes data.

    Args:
        blob_name (str): The name of the blob in GCS. (Ex. path/to/file.ext)
    """
    logger.info("Loading file from GCS...")
    logger.info(f"{blob_name=}")

    return get_file(
        gcs_file_path=blob_name,
        bucket_name=tts_config._CLOUD_PROVIDER.BUCKET_NAME,
    )


def list_files_in_gcs_bucket() -> list[str]:
    """
    List all files in a GCS folder.

    Returns:
        list[str]: A list of file names in the specified GCS folder.
    """
    logger.info("Listing files in GCS bucket...")

    bucket_name = tts_config._CLOUD_PROVIDER.BUCKET_NAME
    logger.info(f"{bucket_name=}")

    return list_blobs(bucket_name=bucket_name)
