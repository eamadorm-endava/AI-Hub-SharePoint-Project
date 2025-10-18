import wave
from google import genai
from google.genai import types
from agent.tools.config import TTSToolConfig


tts_config = TTSToolConfig()
genai_client = genai.Client(api_key=tts_config.GEMINI_API_KEY.get_secret_value())


# Code adapted from: https://ai.google.dev/gemini-api/docs/speech-generation


# Set up the wave file to save the output:
def wave_file(file_name, pcm, channels=1, rate=24000, sample_width=2):
    """
    Saves PCM audio data to a WAV file.
    Args:
        file_name (str): The name of the output WAV file.
        pcm (bytes): The PCM audio data.
        channels (int): Number of audio channels. Default is 1 (mono).
        rate (int): Sample rate in Hz. Default is 24000.
        sample_width (int): Sample width in bytes. Default is 2 (16-bit audio).

    Returns:
        None
    """
    with wave.open(file_name, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def generate_single_speaker_tts_audio(
    text: str, text_tone: str = "cheerfully", file_name: str = "output.wav"
) -> None:
    """
    Generates audio from text using the Gemini TTS API and saves it to a file.

    Args:
        text (str): The text to be converted into speech.
        text_tone (str): The tone in which the text should be spoken.

    Returns:
        None
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

    wave_file(file_name, audio_data)


def generate_multi_speaker_tts_audio(text: str, file_name: str = "output.wav") -> None:
    """
    Generates multi-speaker audio from text using the Gemini TTS API and saves it to a file.

    Args:
        text (str): The text to be converted into speech.
        text_tone (str): The tone in which the text should be spoken.
        file_name (str): The name of the output WAV file.

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

    wave_file(file_name, audio_data)  # Saves the file to current directory
