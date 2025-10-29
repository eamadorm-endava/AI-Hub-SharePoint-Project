from loguru import logger
from utils.gcp.gcs import get_file, list_blobs, upload_bytes
from .config import GCSToolConfig
from .schemas import Blob, TextBlob


gcs_config = GCSToolConfig()


def upload_text_to_gcs(blob_data: TextBlob) -> None:
    """
    Wrapper function to upload text files into GCS

    Args:
        upload_request: TextBlob -> Class containing the required parameters
                                    for the upload, with input validations

    Returns:
        None
    """
    logger.info("Uploading text to GCS...")

    blob_name = blob_data.name
    text = blob_data.text

    logger.debug(f"{blob_name = }")

    try:
        upload_bytes(
            bytes_data=text.encode("UTF-8"),
            blob_name=blob_name,
            bucket_name=gcs_config._CLOUD_PROVIDER.BUCKET_NAME,
            content_type=gcs_config.CONTENT_TYPE,
        )
    except Exception as e:
        logger.error(f"An error while uploading text to GCS occurred: {e}")
        return

    logger.info("Text successfully uploaded to GCS")


def load_text_file_from_gcs(blob_data: TextBlob) -> TextBlob:
    """
    Load a text file from GCS into memory (as string).

    Args:
        blob_data: TextBlob -> Object containing the path and name of the text file

    Return:
        TextBlob -> The same TextBlob object in blob_data, but uploaded with its content
    """
    logger.info("Loading file from GCS...")

    blob_name = blob_data.name
    logger.info(f"{blob_name=}")

    try:
        string_bytes = get_file(
            gcs_file_path=blob_name,
            bucket_name=gcs_config._CLOUD_PROVIDER.BUCKET_NAME,
        )

    except Exception as e:
        logger.error(f"Error loading text file from GCS: {e}")

    blob_data.text = string_bytes.decode("UTF-8")

    logger.info("File successfully loaded from GCS")

    return blob_data


def list_files_in_gcs_bucket() -> list[Blob]:
    """
    List all files in a GCS folder.

    Returns:
        list[Blob]: A list Blobs containing different information about the data in GCS.
    """
    logger.info("Listing files in GCS bucket...")

    bucket_name = gcs_config._CLOUD_PROVIDER.BUCKET_NAME

    list_blobs_raw = list_blobs(bucket_name=bucket_name)

    list_of_blobs = [Blob(**blob) for blob in list_blobs_raw]

    return list_of_blobs
