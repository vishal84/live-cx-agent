import os
import logging
import vertexai
from pathlib import Path
from dotenv import load_dotenv

from agent import adk_app

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

client = vertexai.Client(
  project=os.getenv("GOOGLE_CLOUD_PROJECT"),
  location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

# If you don't have an Agent Engine instance already, create an instance.
agent_engine = client.agent_engines.create()

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(agent_engine.api_resource.name.split("/")[-1])

client.agent_engines.update(
    name=agent_engine.api_resource.name,
    agent=adk_app,
    config={
      "display_name": "Live CX Agent",
      "staging_bucket": "gs://kpmg-agents-agent-engine",
      "gcs_dir_name": "live-cx-agent",
      "agent_framework": "google-adk",
      "requirements_file": "./requirements.txt",
      "extra_packages": ["agent/agent.py"]
    },
)