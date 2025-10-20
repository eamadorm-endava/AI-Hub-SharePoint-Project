from loguru import logger
import wave
from io import BytesIO
from google import genai
from google.genai import types
from agent.tools.config import TTSToolConfig
from utils.gcp.gcs import upload_bytes


tts_config = TTSToolConfig()

genai_client = genai.Client(api_key=tts_config.GEMINI_API_KEY.get_secret_value())


# Code adapted from: https://ai.google.dev/gemini-api/docs/speech-generation
# Set up the wave file:
def pcm_to_wav_bytes(
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


def single_speaker_tts_audio(text: str) -> bytes:
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
    wav_bytes = pcm_to_wav_bytes(audio_data)

    return wav_bytes


def multi_speaker_tts_audio(text: str) -> bytes:
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
    wav_bytes = pcm_to_wav_bytes(audio_data)

    return wav_bytes


def text_to_speech(
    title: str,
    text: str,
    mode: str,
    gcs_path: str = tts_config.GCS_PATH,
) -> str | None:
    """
    Orchestrator function that generates the single speaker audio and stores it into GCS

    Args:
        title: str -> Title of the audio generated. (e.g. my_audio)
        text: str -> The text to be converted into speech.
        gcs_path: str -> Path where the audio will be stored in gcs. (e.g. audio/)
        mode: str -> Either 'single' or 'multi' speakers

    Returns:
        gcs_audio_path: Path where the audio was stored
    """
    logger.info("Using Text to Speech Tool...")

    if not all(
        isinstance(param, str) and param.strip() != ""
        for param in [title, gcs_path, text]
    ):
        logger.error(
            "Parameters: title, gcs_path, and text must be non-null strings, "
            f"got {type(title)}, {type(gcs_path)}, {type(text)}"
        )
        return
    if mode not in ["single", "multi"]:
        logger.error(
            "'mode' can only accept 'single' or 'multi', related to the number of speakers in the audio"
        )
        return

    audio_generation = {
        "single": single_speaker_tts_audio,
        "multi": multi_speaker_tts_audio,
    }

    # Cleaning the parameters
    title = title.strip().lower().replace(" ", "_").replace(".", "")

    gcs_path = gcs_path.rstrip("/")

    full_gcs_path = f"{gcs_path}/{title}.wav"

    logger.debug(f"{title =}")
    logger.debug(f"{text =}")
    logger.debug(f"{gcs_path =}")
    logger.debug(f"{full_gcs_path =}")

    logger.debug("Creating audio...")
    try:
        audio_bytes = audio_generation[mode](text=text)
    except Exception as e:
        logger.error(f"An error occured while generating audio with Gemini TTS: {e}")
    logger.debug("Audio successfully created")

    logger.debug("Storing audio bytes into GCS")
    upload_bytes(
        bytes_data=audio_bytes,
        blob_name=full_gcs_path,
        content_type="audio/wav",
        bucket_name=tts_config._CLOUD_PROVIDER.BUCKET_NAME,
    )

    gcs_audio_path = f"gs://{tts_config._CLOUD_PROVIDER.BUCKET_NAME}/{full_gcs_path}"
    logger.info(f"Audio stored in {gcs_audio_path}")

    return gcs_audio_path
