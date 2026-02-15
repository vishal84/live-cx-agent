#%%
import os
import asyncio
import logging
import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp
from agent import root_agent
from dotenv import load_dotenv

local_agent = AdkApp(
    agent=root_agent,
    enable_tracing=True
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

display_name="Live CX Agent"
GOOGLE_CLOUD_PROJECT=str(os.getenv("GOOGLE_CLOUD_PROJECT"))
GOOGLE_CLOUD_LOCATION=str(os.getenv("GOOGLE_CLOUD_LOCATION"))
STAGING_BUCKET=str(os.getenv("STAGING_BUCKET"))

vertexai.init(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
  staging_bucket=STAGING_BUCKET
)

client = vertexai.Client(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION,
)

# If you don't have an Agent Engine instance already, create an instance.
remote_app = client.agent_engines.create(
  agent=local_agent,
  config=dict(
    display_name=f"{display_name}",
    description="A cx agent that transfer to a live chat.",
    gcs_dir_name="live-cx-agent",
    agent_framework="google-adk",
    extra_packages=["./agent.py"],
    requirements=[
      "google-cloud-aiplatform[adk,agent_engines]"
    ],
    staging_bucket=STAGING_BUCKET,
  ),
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(remote_app.api_resource.name.split("/")[-1])

#%%
# Test on Agent Engine
deploy_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{display_name}"')]
deploy_agent = agent_engines.get(deploy_agent[0])
print(deploy_agent)
# async def remote_send_message(prompt: str):
#     session = await deployed_agent.async_create_session(user_id="cx_user")
#     async for event in deployed_agent.async_stream_query(
#       user_id="cx_user",
#       session_id=session["id"],
#       message=prompt,
#     ):
#         print(event)

# asyncio.run(remote_send_message("What is the date and time?"))

# %%
