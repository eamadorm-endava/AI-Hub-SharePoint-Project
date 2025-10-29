from loguru import logger
from google import genai
from google.genai import types
import asyncio
from .config import ImaGenToolConfig
from .schemas import ImaGenRequest, Image
from utils.gcp.gcs import upload_bytes

imagen_config = ImaGenToolConfig()

genai_client = genai.Client(api_key=imagen_config.GEMINI_API_KEY.get_secret_value())


async def _generate_image(
    prompt: str,
    general_image_name: str,
    llm_model: str = imagen_config.MODEL_NAME,
    gcs_path: str = imagen_config.GCS_PATH,
) -> Image:
    """
    Calls a GenAI model exclusively for image generation based on text (prompt)

    Args:
        prompt:str -> Text describing the image to generate
        general_image_name: str -> General image name. Ex "waves_in_the_sea"
        llm_model: str -> Name of the model used to generate the images
        gcs_path: str -> The path within the GCS bucket where the image should be stored (Ex: 'my_folder').

    Returns:
        Image -> Image object containing the image data
    """

    logger.debug(f"{general_image_name = }")
    logger.debug(f"Input {prompt = }")
    logger.debug(f"{gcs_path = }")

    image_data = Image(prompt=prompt, image_name=general_image_name)

    # Code adapted from: https://googleapis.github.io/python-genai/#imagen
    # If you want async behaviour, just add call client.aio.<module to use>
    response = await genai_client.aio.models.generate_images(
        model=llm_model,
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=imagen_config.DEFAULT_GENERATED_IMAGES,
        ),
    )

    try:
        image_data.image_bytes = response.generated_images[0].image.image_bytes
        image_data.gcs_path = f"{gcs_path.strip('/')}/{general_image_name}.png"
    except Exception as e:
        error_message = f"Eror while fetching the image: {e}"
        logger.error(error_message)
        return error_message

    logger.debug("Image generated successfully")
    return image_data


async def generate_images(image_requests: list[ImaGenRequest]) -> list[Image]:
    """
    Generates n number of images based on n number of requests

    Args:
        image_requests: list[ImaGenRequest] -> List of ImaGenRequest objects

    Returns:
        list[Image] -> A list of Image objects, which contains the public URL to access the image generated
    """
    logger.info("Using Image Generation Tool...")

    if not isinstance(image_requests, list):
        error_message = "Parameter image_requests must be a list"
        logger.error(error_message)
        return error_message  # Agent could read this error and try to fix how this tool is used by him
    elif len(image_requests) < 1:
        error_message = "Parameter image_requests must have at least one entry"
        logger.error(error_message)
        return error_message

    logger.info(f"Generating {len(image_requests)} images...")

    logger.debug(f"{image_requests = }")
    # Creating a list of generation tasks
    generation_tasks = list()

    logger.debug("Preparing generation requests")
    for image_request in image_requests:
        task = _generate_image(
            prompt=image_request.prompt, general_image_name=image_request.image_name
        )
        generation_tasks.append(task)

    logger.debug("Launching concurrent generation")

    # images_data is a list of Image objects
    images_data = await asyncio.gather(*generation_tasks)

    # As upload_bytes is a syncronus function, it will be executed in
    # different threads to reduce the execution time
    storage_tasks = list()
    for image_data in images_data:
        # task is a function
        task = asyncio.to_thread(
            upload_bytes,
            image_data.gcs_path,  # First argument of the function - blob_name
            imagen_config._CLOUD_PROVIDER.BUCKET_NAME,  # Bucket name parameter
            imagen_config.CONTENT_TYPE,  # Content type parameter
            image_data.image_bytes,  # Bytes data parameter
            True,  # last argument, make the gcs blob public, to return the image urls
        )

        storage_tasks.append(task)

    # A list of what the task return, in this case, a list of image urls
    images_urls = await asyncio.gather(*storage_tasks, return_exceptions=True)

    for image_index, image_data in enumerate(images_data):
        image_data.public_url = images_urls[image_index]
        image_data.image_bytes = None  # To not send all the image bytes to the AI Agent

    logger.info("Images successfully generated")

    return images_data
