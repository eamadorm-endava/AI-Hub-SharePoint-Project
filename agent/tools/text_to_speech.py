import wave
from io import BytesIO
from google import genai
from google.genai import types
from agent.tools.config import TTSToolConfig


tts_config = TTSToolConfig()
genai_client = genai.Client(api_key=tts_config.GEMINI_API_KEY.get_secret_value())


# Code adapted from: https://ai.google.dev/gemini-api/docs/speech-generation


# Set up the wave file:
def pcm_to_wav_bytes(
    pcm_data: bytes, sample_rate: int = 24000, channels: int = 1
) -> BytesIO:
    """
    Converts PCM audio data (returned from Gemini TTS) to WAV format and returns it as a BytesIO object.

    Args:
        pcm_data (bytes): The PCM audio data.
        sample_rate (int): The sample rate of the audio data.
        channels (int): The number of audio channels.

    Returns:
        BytesIO: The WAV audio data in a BytesIO object.
    """
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit PCM → 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_data)
    buffer.seek(0)
    return buffer


def generate_single_speaker_tts_audio(
    text: str, text_tone: str = "cheerfully"
) -> BytesIO:
    """
    Generates audio from text using the Gemini TTS API and returns the audio data.

    Args:
        text (str): The text to be converted into speech.
        text_tone (str): The tone in which the text should be spoken.

    Returns:
        bytesIO: The generated audio data converted to WAV format (bytes).
    """
    # Create the TTS request
    response = genai_client.models.generate_content(
        model=tts_config.TTS_MODEL,
        contents=f" Please say this {text_tone}: {text}",
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
    wav_bytes = pcm_to_wav_bytes(audio_data)

    return wav_bytes


def generate_multi_speaker_tts_audio(text: str) -> BytesIO:
    """
    Generates multi-speaker audio from text using the Gemini TTS API and returns the audio data.

    Args:
        text (str): The text to be converted into speech. Ex: "Speaker 1: Hello! Speaker 2: Hi there!"

    Returns:
        None
    """

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
    wav_bytes = pcm_to_wav_bytes(audio_data)

    return wav_bytes
