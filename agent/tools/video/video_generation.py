from loguru import logger
import time
import os
import shutil
from moviepy import ImageClip
from google import genai
from google.genai import types
from typing import Literal
from .config import VideoGenToolConfig, PodcastVideoConfig
from .schemas import VideoGenRequest, VideoGenResponse, PodcastVideoRequest
from utils.gcp.gcs import upload_bytes, get_file, upload_file
from ..audio.audio_data import _get_audio


video_config = VideoGenToolConfig()
podcast_config = PodcastVideoConfig()

genai_client = genai.Client(api_key=video_config.GEMINI_API_KEY.get_secret_value())


# Code adapted from: https://ai.google.dev/gemini-api/docs/video?example=dialogue#veo-model-parameters
# To obtain the bytes of the video, check the documentation: https://googleapis.github.io/python-genai/#veo
def _generate_single_video(
    prompt: str,
    aspect_ratio: Literal["9:16", "16:9"],
    duration_seconds: Literal[5, 6, 8],
) -> bytes:
    """
    Generate a video with no audio using a Gemini Model.

    Args:
        prompt: str -> Prompt defining what the video will be about
        aspect_ratio: Literal["9:16", "16:9"] -> Aspect ratio of the video, either "9:16" or "16:9"
        duration_seconds: Literal[5, 6, 8] -> Duration of the video, either 5, 6, or 8.

    Return:
        bytes -> Bytes of the video generated
    """
    operation = genai_client.models.generate_videos(
        model=video_config.VIDEO_MODEL,
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
        ),
    )

    # Poll the operation status until the video is ready.
    while not operation.done:
        logger.info("Waiting for video generation to complete...")
        time.sleep(10)
        operation = genai_client.operations.get(operation)

    # Get the generated video.
    generated_video = operation.response.generated_videos[0]

    # Download and stores the video bytes into the video object
    # Check: https://googleapis.github.io/python-genai/genai.html#genai.files.Files.download
    genai_client.files.download(file=generated_video.video)

    video_bytes = generated_video.video.video_bytes

    return video_bytes


def generate_video(video_request: VideoGenRequest) -> VideoGenResponse:
    """
    Orchestrator Function that generates the video, store it in GCS, and retrieves the video's public URL

    Args:
        video_request -> VideoGenRequest object containing the info to generate the video

    Returns:
        VideoGenResponse: Class with a public URL where the video can be obtained
    """
    logger.info("Generating video...")
    logger.debug(f"title = {video_request.title}")
    logger.debug(f"prompt = {video_request.prompt}")
    logger.debug(f"aspect_ratio = {video_request.aspect_ratio}")
    logger.debug(f"duration_seconds = {video_request.duration_seconds}")

    video_bytes = _generate_single_video(
        prompt=video_request.prompt,
        aspect_ratio=video_request.aspect_ratio,
        duration_seconds=video_request.duration_seconds,
    )
    logger.info("Video successfully generated, storing it into GCS...")

    blob_name = f"{video_config.GCS_PATH.strip('/')}/{video_request.title}.mp4"
    logger.debug(f"{blob_name = }")

    video_url = upload_bytes(
        bytes_data=video_bytes,
        blob_name=blob_name,
        bucket_name=video_config._CLOUD_PROVIDER.BUCKET_NAME,
        content_type=video_config.GCS_CONTENT_TYPE,
        make_public=True,
    )
    logger.info(f"Video successfully stored in GCS: {video_url}")

    result = VideoGenResponse(video_url=video_url)

    return result


def generate_podcast_video(video_request: PodcastVideoRequest) -> None:
    """
    Orchestration function that adds a cover image to the podcast audio,
    stores it into Google Cloud Storage
    """
    logger.info("Generating podcast video...")

    gcs_audio_path = video_request.gcs_audio_path
    audio_extension = gcs_audio_path.split(".")[-1]

    logger.debug(f"{gcs_audio_path = }")

    logger.debug("Getting audio...")
    audio = _get_audio(audio_path=gcs_audio_path)

    logger.debug("Getting cover image...")
    image_bytes = get_file(
        gcs_file_path=podcast_config.COVER_IMAGE,
        bucket_name=video_config._CLOUD_PROVIDER.BUCKET_NAME,
    )

    logger.debug("Creating podcast video...")
    image = ImageClip(image_bytes).with_duration(audio.duration)

    video = image.with_audio(audio)

    logger.debug("Saving the podcast video...")

    temp_local_storage = podcast_config.TEMP_LOCAL_STORAGE.strip("/")
    podcast_name = gcs_audio_path.split("/")[-1].replace(audio_extension, "mp4")

    if not os.path.isdir(temp_local_storage):
        os.makedirs(temp_local_storage)

    temp_file = f"{temp_local_storage}/{podcast_name}"
    video.write_videofile(
        temp_file,
        fps=60,
    )

    gcs_video_path = podcast_config.GCS_PATH.strip("/")
    upload_file(
        origin_file_path=temp_file,
        destination_file_path=f"{gcs_video_path}/{podcast_name}",
        bucket_name=video_config._CLOUD_PROVIDER.BUCKET_NAME,
    )

    # os does not allow to remove a folder if its not empty, shutil does
    shutil.rmtree(temp_local_storage)
