import os
import asyncio
import logging
import vertexai
from vertexai import agent_engines
from vertexai.agent_engines import AdkApp
from agent.agent import root_agent
from dotenv import load_dotenv, dotenv_values, set_key

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

# Create on Agent Engine
remote_app = client.agent_engines.create(
  agent=local_agent,
  config=dict(
    agent_framework="google-adk",
    display_name=DISPLAY_NAME,
    description="A cx agent that transfer to a live chat.",
    gcs_dir_name="live-cx-agent",
    staging_bucket=STAGING_BUCKET,
    extra_packages=["./agent"],
    requirements=[
      "google-cloud-aiplatform[adk,agent_engines]",
      "python-dotenv>=1.0.0",
      "google-cloud-storage"
    ],
    env_vars={
      "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
      "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
      "TOPIC_ID": TOPIC_ID
    },
  ),
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(remote_app.api_resource.name.split("/")[-1])

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
asyncio.run(remote_send_message("What is the date and time?"))

def update_env_file(agent_engine_id, env_file_path):
  """Updates the .env file with the agent engine ID."""
  try:
    set_key(env_file_path, "AGENT_ENGINE_ID", agent_engine_id)
    print(f"Updated AGENT_ENGINE_ID in {env_file_path} to {agent_engine_id}")
  except Exception as e:
    print(f"Error updating .env file: {e}")

# log remote_app
logging.info(
    f"Deployed agent to Vertex AI Agent Engine successfully, resource name: {remote_app.resource_name}"
)

# Update the .env file with the new Agent Engine ID
update_env_file(remote_app.resource_name, env_path)
# # %%
# # Update on Agent Engine
# remote_agent = [agent.resource_name for agent in agent_engines.list(filter=f'display_name="{DISPLAY_NAME}"')]
# remote_agent = agent_engines.get(remote_agent[0])

# remote_agent.update(
#     requirements=[
#       "google-cloud-aiplatform[adk,agent_engines]",
#       "python-dotenv>=1.0.0",
#       "google-cloud-storage"
#     ],
#     extra_packages=["../agent"])