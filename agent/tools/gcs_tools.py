from io import BytesIO
from utils.gcp.gcs import upload_bytes
from agent.tools.config import TTSToolConfig


tts_config = TTSToolConfig()


def upload_bytes_to_gcs(bytes_data: BytesIO, blob_name: str, content_type: str) -> None:
    """
    Wrapper function to upload bytes data to GCS.

    Args:
        bytes_data (BytesIO): The bytes data to upload.
        blob_name (str): The name of the blob in GCS. (Ex. path/to/file.ext)
        content_type (str): The content type of the data. (Ex. "audio/wav", "image/png", "application/pdf", "text/plain")
    """
    upload_bytes(
        blob_name=blob_name,
        bucket_name=tts_config._CLOUD_PROVIDER.BUCKET_NAME,
        content_type=content_type,
        bytes_data=bytes_data,
    )
