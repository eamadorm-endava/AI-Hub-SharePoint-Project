from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from loguru import logger
import sys

sys.path.append("..")

from agent.config import AgentConfig


agent_config = AgentConfig()

# To load the Gemini API key from GCP Secret Manager
agent_config.load_gemini_api_key()

provider = GoogleProvider(api_key=agent_config.GEMINI_API_KEY.get_secret_value())
model = GoogleModel(model_name=agent_config.GEMINI_MODEL_NAME, provider=provider)
model_settings = GoogleModelSettings(temperature=agent_config.MODEL_TEMPERATURE)

agent = Agent(model=model, model_settings=model_settings)


# This will execute the agent on the local console
if __name__ == "__main__":
    logger.info("Starting Agent chat...")
    request = input("Introduce a query (To exit, enter 'exit'):").strip()
    history = []
    while request != "exit":
        result = agent.run_sync(request, message_history=history)
        history = result.all_messages()  # list of ModelRequest objects
        history_json = result.all_messages_json()
        logger.debug(f"{history_json=}")
        logger.info(f"{result.output}")
        request = input("Introduce a query (To exit, enter 'exit'):").strip()
