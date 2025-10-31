import os
import shutil
from loguru import logger
from moviepy import AudioFileClip
from utils.gcp.gcs import download_file
from .schemas import AudioDurationRequest, AudioDurationResponse
from .config import AudioConfig


audio_config = AudioConfig()


def _get_audio(audio_path: str) -> AudioFileClip:
    """
    Gets the duration of a .wav audio file

    Args:
        audio_path: str -> gcs path to the bucket (e.g. path/to/file.wav)

    Return:
        AudioFileClip -> Object that allows use the audio and get some of is attributes
    """
    logger.debug("Downloading file...")

    # Generating temporal paths
    temp_local_blob = f"{audio_config.TEMP_LOCAL_STORAGE.strip('/')}/{audio_path}"
    temp_local_file_path = "/".join(temp_local_blob.split("/")[:-1])

    if not os.path.isdir(temp_local_file_path):
        os.makedirs(temp_local_file_path)

    download_file(
        gcs_file_path=audio_path,
        local_file_path=temp_local_blob,
        bucket_name=audio_config._CLOUD_PROVIDER.BUCKET_NAME,
    )

    logger.debug("Loading audio from temporal location...")
    audio = AudioFileClip(temp_local_blob)

    logger.debug("Deleting audio from temporal location...")
    # os does not allow to remove a folder if its not empty, shutil does
    shutil.rmtree(temp_local_file_path)

    return audio


def get_audio_duration(audio_request: AudioDurationRequest) -> AudioDurationResponse:
    """
    Orchestration function to retrieve the AudioBlob object containing the
    gcs path to a wav file, and returns its duration.

    Args:
        audio_request: AudioDurationRequest -> Object containing the data required by
                                            the request

    Returns:
        AudioDurationResponse ->
    """
    logger.info("Using get_audio_duration tool...")

    logger.debug(f"gcs_audio_path = {audio_request.name}")
    audio = _get_audio(audio_path=audio_request.name)

    output = AudioDurationResponse(
        name=audio_request.name,
        duration_seconds=audio.duration,
    )

    return output
