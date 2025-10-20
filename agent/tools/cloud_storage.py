from loguru import logger
from utils.gcp.gcs import get_file, list_blobs, upload_bytes
from agent.config import GCPConfig


gcp_config = GCPConfig()


def upload_text_to_gcs(text: str, blob_name: str) -> None:
    """
    Wrapper function to upload text files into GCS

    Args:
        text: str -> Text to be stored in GCS
        blob_name: str -> Name of the blob (e.g. gcs_path/file_name.txt)

    Returns:
        None
    """
    upload_bytes(
        bytes_data=text.encode("UTF-8"),
        blob_name=blob_name,
        bucket_name=gcp_config.BUCKET_NAME,
        content_type="text/plain",
    )


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
        bucket_name=gcp_config.BUCKET_NAME,
    )


def list_files_in_gcs_bucket() -> list[str]:
    """
    List all files in a GCS folder.

    Returns:
        list[str]: A list of file names in the specified GCS folder.
    """
    logger.info("Listing files in GCS bucket...")

    bucket_name = gcp_config.BUCKET_NAME
    logger.info(f"{bucket_name=}")

    return list_blobs(bucket_name=bucket_name)
