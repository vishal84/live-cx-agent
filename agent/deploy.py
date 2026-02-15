import os
import logging
from pathlib import Path
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

GOOGLE_CLOUD_PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")
# AGENT_ENGINE_ID=os.getenv("AGENT_ENGINE_ID")
TOPIC_ID=os.getenv("TOPIC_ID")

# Initialize Vertex AI SDK
vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

client = vertexai.Client(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION
)

from .agent import root_agent

# If you don't have an Agent Engine instance already, create an instance.
agent_engine_app = agent_engines.create(
  agent_engine=root_agent,
  display_name="live-cx-agent",
  description="Live CX Agent",
  env_vars=[
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
    # "AGENT_ENGINE_ID",
    "TOPIC_ID"
  ],
  requirements=[
        "google-adk>=1.21.0",
        "python-dotenv>=1.0.0",
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-vertexai"
    ],
    gcs_dir_name="live-cx-agent"
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(agent_engine_app.api_resource.name.split("/")[-1])

