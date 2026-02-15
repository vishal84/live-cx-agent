 #%%
import os
import asyncio
import logging
import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp
from agent import root_agent
from dotenv import load_dotenv, dotenv_values

local_agent = AdkApp(
    agent=root_agent,
    enable_tracing=True
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)
env_vars = dotenv_values(dotenv_path=env_path)

DISPLAY_NAME=env_vars.get("DISPLAY_NAME")
TOPIC_ID=env_vars.get("TOPIC_ID")
GOOGLE_CLOUD_PROJECT=env_vars.get("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=env_vars.get("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET=env_vars.get("STAGING_BUCKET")

vertexai.init(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
  staging_bucket=STAGING_BUCKET
)

client = vertexai.Client(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
)

#%% Create on Agent Engine
# If you don't have an Agent Engine instance already, create an instance.
remote_app = client.agent_engines.create(
  agent=local_agent,
  config=dict(
    display_name=DISPLAY_NAME,
    description="A cx agent that transfer to a live chat.",
    gcs_dir_name="live-cx-agent",
    agent_framework="google-adk",
    extra_packages=["./agent.py"],
    requirements=[
      "google-cloud-aiplatform[adk,agent_engines]",
      "python-dotenv>=1.0.0",
      "google-cloud-storage"
    ],
    staging_bucket=STAGING_BUCKET,
    env_vars={
      "TOPIC_ID": TOPIC_ID
    },
  ),
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(remote_app.api_resource.name.split("/")[-1])

#%%
# Test on Agent Engine
deployed_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"')]
deployed_agent = agent_engines.get(deployed_agent[0])
async def remote_send_message(prompt: str):
    session = await deployed_agent.async_create_session(user_id="cx_user")
    async for event in deployed_agent.async_stream_query(
      user_id="cx_user",
      session_id=session["id"],
      message=prompt,
    ):
      print(event)

# This will work as its running in a jupyter kernel.
await remote_send_message("What is the date and time?")

# %%
# Update the deployed agent on Agent Engine
remote_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"')]
remote_agent = agent_engines.get(remote_agent[0])

remote_agent.update(
    requirements=[
      "google-cloud-aiplatform[adk,agent_engines]",
      "python-dotenv>=1.0.0",
      "google-cloud-storage"
    ],
    extra_packages=["./agent.py"])
# %%
