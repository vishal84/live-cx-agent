import os
import sys
import logging
import vertexai
from agent.agent import root_agent
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

GOOGLE_CLOUD_PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET=os.getenv("STAGING_BUCKET")

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
  agent=root_agent,
  config=dict(
    display_name="Search Agent",
    description="A production agent that can search the web for current information",
    gcs_dir_name="live-cx-agent",
    agent_framework="google-adk",
    requirements_file="agent/requirements.txt",
    extra_packages=["agent"],
    staging_bucket=STAGING_BUCKET,
  ),
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(remote_app.api_resource.name.split("/")[-1])
