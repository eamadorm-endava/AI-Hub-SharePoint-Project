from pydantic_ai import Agent, Tool
from pydantic_ai.models.google import GoogleModel, GoogleModelSettings
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.mcp import load_mcp_servers
from loguru import logger
from agent.config import AgentConfig
from agent.tools import (
    load_text_file_from_gcs,
    list_files_in_gcs_bucket,
    upload_text_to_gcs,
    text_to_speech,
    generate_images,
    query_news_table,
    generate_video,
)
from agent.auxiliars import load_system_prompt

raw_tools = [
    load_text_file_from_gcs,
    list_files_in_gcs_bucket,
    upload_text_to_gcs,
    text_to_speech,
    generate_images,
    query_news_table,
    generate_video,
]

agent_config = AgentConfig()

system_prompt = load_system_prompt()

# To load the Gemini API key from GCP Secret Manager
agent_config.load_gemini_api_key()

provider = GoogleProvider(api_key=agent_config.GEMINI_API_KEY.get_secret_value())
model = GoogleModel(model_name=agent_config.GEMINI_MODEL_NAME, provider=provider)
model_settings = GoogleModelSettings(temperature=agent_config.MODEL_TEMPERATURE)

servers = load_mcp_servers("agent/mcp_config.json")

agent = Agent(
    model=model,
    model_settings=model_settings,
    system_prompt=system_prompt,
    toolsets=servers,
    tools=[Tool(tool) for tool in raw_tools],
)


# This will execute the agent on the local console
if __name__ == "__main__":
    logger.info("Starting Agent chat...")
    request = input("Introduce a query (To exit, enter 'exit'):").strip()
    history = []
    while request != "exit":
        result = agent.run_sync(request, message_history=history)
        history = result.all_messages()  # list of ModelRequest objects
        history_json = result.all_messages_json()
        # logger.debug(f"{history_json=}")
        logger.info(f"{result.output}")
        request = input("Introduce a query (To exit, enter 'exit'):").strip()
