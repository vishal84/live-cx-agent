import os
import asyncio
import logging
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv, dotenv_values, set_key

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)
env_vars = dotenv_values(dotenv_path=env_path)

DISPLAY_NAME=env_vars.get("DISPLAY_NAME")
GOOGLE_CLOUD_PROJECT=env_vars.get("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=env_vars.get("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET=env_vars.get("STAGING_BUCKET")
AGENT_ENGINE_ID=env_vars.get("AGENT_ENGINE_ID")

vertexai.init(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
  staging_bucket=STAGING_BUCKET
)

client = vertexai.Client(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
)

agent_engine=client.agent_engines.get(name=AGENT_ENGINE_ID)

# Test on Agent Engine
async def remote_send_message(prompt: str):
    session = await agent_engine.async_create_session(user_id="cx_user")
    async for event in agent_engine.async_stream_query(
      user_id="cx_user",
      session_id=session["id"],
      message=prompt,
    ):
      print(event)

# This will work as its running in a jupyter kernel.
asyncio.run(remote_send_message("What is the date and time?"))