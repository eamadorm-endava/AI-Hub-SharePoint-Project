from loguru import logger
import wave
from io import BytesIO
from google import genai
from google.genai import types
from .config import AudioConfig
from .schemas import TTSRequest, TTSResponse
from utils.gcp.gcs import upload_bytes


tts_config = AudioConfig()

genai_client = genai.Client(api_key=tts_config.GEMINI_API_KEY.get_secret_value())


# Code adapted from: https://ai.google.dev/gemini-api/docs/speech-generation
# Set up the wave file:
def _pcm_to_wav_bytes(
    pcm_data: bytes, sample_rate: int = 24000, channels: int = 1
) -> bytes:
    """
    Converts PCM audio data (returned from Gemini TTS) to WAV format and returns it as a BytesIO object.

    Args:
        pcm_data (bytes): The PCM audio data.
        sample_rate (int): The sample rate of the audio data.
        channels (int): The number of audio channels.

    Returns:
        bytes: The WAV audio data in bytes.
    """
    buffer = BytesIO()

    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit PCM → 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)

    buffer.seek(0)

    return buffer.getvalue()  # Return bytes data


def _single_speaker_tts_audio(text: str) -> bytes:
    """
    Generates audio from text using the Gemini TTS API and returns the audio data.

    Args:
        text: str -> The text to be converted into speech.

    Returns:
        bytes: The generated audio data converted to WAV format (bytes).
    """
    logger.info("Generating single-speaker TTS audio...")

    # Create the TTS request
    response = genai_client.models.generate_content(
        model=tts_config.TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=tts_config.FIRST_SPEAKER_VOICE,
                    )
                )
            ),
        ),
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data

    # Convert PCM to WAV bytes
    logger.debug("Converting PCM to WAV bytes...")
    wav_bytes = _pcm_to_wav_bytes(audio_data)

    return wav_bytes


def _multi_speaker_tts_audio(text: str) -> bytes:
    """
    Generates multi-speaker audio from text using the Gemini TTS API and returns the audio data.

    Args:
        text (str): The text to be converted into speech. Ex: "Speaker 1: Hello! Speaker 2: Hi there!"

    Returns:
        bytes: The generated audio data converted to WAV format (bytes).
    """
    logger.info("Generating multi-speaker TTS audio...")
    response = genai_client.models.generate_content(
        model=tts_config.TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker=tts_config.FIRST_SPEAKER_NAME,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=tts_config.FIRST_SPEAKER_VOICE,
                                )
                            ),
                        ),
                        types.SpeakerVoiceConfig(
                            speaker=tts_config.SECOND_SPEAKER_NAME,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=tts_config.SECOND_SPEAKER_VOICE,
                                )
                            ),
                        ),
                    ]
                )
            ),
        ),
    )

    audio_data = response.candidates[0].content.parts[0].inline_data.data

    # Convert PCM to WAV bytes
    logger.debug("Converting PCM to WAV bytes...")
    wav_bytes = _pcm_to_wav_bytes(audio_data)

    return wav_bytes


def text_to_speech(tts_request: TTSRequest) -> TTSResponse:
    """
    Orchestrator function that generates the single speaker audio and stores it into GCS

    Args:
        tts_request: TTSRequest -> Class containing the parameters to create the speech

    Returns:
        gcs_audio_path: Path where the audio was stored
    """
    logger.info("Using Text to Speech Tool...")

    audio_generation = {
        "single": _single_speaker_tts_audio,
        "multi": _multi_speaker_tts_audio,
    }

    title = tts_request.title
    text = tts_request.text
    gcs_path = tts_config.GCS_PATH.rstrip("/")
    mode = tts_request.mode
    full_gcs_path = f"{gcs_path}/{tts_request.title}.wav"

    logger.debug(f"{title = }")
    logger.debug(f"{text = }")
    logger.debug(f"{gcs_path = }")
    logger.debug(f"{mode = }")
    logger.debug(f"{full_gcs_path =}")

    logger.debug("Creating audio...")
    try:
        audio_bytes = audio_generation[mode](text=text)
    except Exception as e:
        logger.error(f"An error occured while generating audio with Gemini TTS: {e}")
    logger.debug("Audio successfully created")

    logger.debug("Storing audio bytes into GCS")
    blob_public_url = upload_bytes(
        bytes_data=audio_bytes,
        blob_name=full_gcs_path,
        content_type="audio/wav",
        bucket_name=tts_config._CLOUD_PROVIDER.BUCKET_NAME,
        make_public=tts_config.PUBLIC_AUDIO,
    )

    if blob_public_url:
        logger.info(f"Blob can be access through: {blob_public_url}")

    output = TTSResponse(
        title=title,
        public_url=blob_public_url,
        full_gcs_path=full_gcs_path,
    )

    return output
