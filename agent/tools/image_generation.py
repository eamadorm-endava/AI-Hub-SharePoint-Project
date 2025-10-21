from loguru import logger
from google import genai
from google.genai import types
import asyncio
from agent.tools.config import ImaGenToolConfig
from utils.gcp.gcs import upload_bytes

imagen_config = ImaGenToolConfig()

genai_client = genai.Client(api_key=imagen_config.GEMINI_API_KEY.get_secret_value())


async def generate_image(
    prompt: str,
    general_image_name: str,
    llm_model: str = imagen_config.MODEL_NAME,
    gcs_path: str = imagen_config.GCS_PATH,
) -> dict:
    """
    Calls a GenAI model exclusively for image generation based on text (prompt)

    Args:
        prompt:str -> Text describing the image to generate
        general_image_name: str -> General image name. Ex "waves_in_the_sea"
        llm_model: str -> Name of the model used to generate the images
        gcs_path: str -> The path within the GCS bucket where the image should be stored (Ex: 'my_folder').

    Returns:
        dict -> Dictionary with the image_name and the image_bytes
    """

    logger.debug(f"{general_image_name = }")
    logger.debug(f"Input {prompt = }")
    logger.debug(f"{gcs_path = }")

    image_data = {}

    # Code adapted from: https://googleapis.github.io/python-genai/#imagen
    # If you want async behaviour, just add call client.aio.<module to use>
    response = await genai_client.aio.models.generate_images(
        model=llm_model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=imagen_config.DEFAULT_GENERATED_IMAGES,
        ),
    )

    image_data["image_name"] = f"{gcs_path.strip('/')}/{general_image_name}.png"
    try:
        image_data["image_bytes"] = response.generated_images[0].image.image_bytes
    except Exception as e:
        logger.error(f"Eror while fetching the image: {e}")
        return

    logger.debug("Image generated successfully")
    return image_data


async def generate_images(prompts_info: list[dict]) -> list[str]:
    """
    Generates n number of images based on n number of requests

    Args:
        requests: list[dict] -> List of dictionaries, each dictianary can be represented as one image generation request
                                The dictionary must contain two keys:
                                        - prompt: Prompt that will generate the image
                                        - image_name: Name of the image

    Returns:
        list[str] -> A list of public urls where the images can be downloaded
    """
    logger.info("Using Image Generation Tool...")

    if not isinstance(prompts_info, list):
        logger.error("prompts_info must be a list")
        return

    elif len(prompts_info) < 1:
        logger.error("prompts_info must have at least one entry")
        return
    elif not all([isinstance(prompt_data, dict) for prompt_data in prompts_info]):
        logger.error("Each entry of the prompts_info parameter must be a dictionary")
        return
    elif not all(
        [
            "prompt" in prompt_data.keys() and "image_name" in prompt_data.keys()
            for prompt_data in prompts_info
        ]
    ):
        logger.error("Each dictionary must contain the keys 'prompt' and 'image_name'")
        return

    logger.info(f"Generating {len(prompts_info)} images...")

    logger.debug(f"{prompts_info = }")
    # Creating a list of generation tasks
    generation_tasks = list()

    logger.debug("Preparing generation requests")
    for request in prompts_info:
        task = generate_image(
            prompt=request["prompt"], general_image_name=request["image_name"]
        )
        generation_tasks.append(task)

    logger.debug("Launching concurrent generation")
    images_data = await asyncio.gather(*generation_tasks)

    # As upload_image_from_memory is a syncronus function, it will be executed in
    # different threads to reduce the execution time
    storage_tasks = list()
    for image_data in images_data:
        task = asyncio.to_thread(
            upload_bytes,
            image_data["image_name"],  # First argument of the function - blob_name
            imagen_config._CLOUD_PROVIDER.BUCKET_NAME,  # Bucket name parameter
            imagen_config.CONTENT_TYPE,  # Content type parameter
            image_data["image_bytes"],  # Bytes data parameter
            True,  # last argument, make the gcs blob public, to return the image urls
        )

        storage_tasks.append(task)

    images_urls = await asyncio.gather(*storage_tasks, return_exceptions=True)

    logger.info("Images Successfully Generated")
    return images_urls
