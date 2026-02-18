import os
import logging
import vertexai
from vertexai import agent_engines, _genai_client
from agent.agent import root_agent
from vertexai.agent_engines import AdkApp
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

# Update on Agent Engine
agent_engine=client.agent_engines.get(name=AGENT_ENGINE_ID)

client.agent_engines.update(
    name=AGENT_ENGINE_ID,
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
            "google-cloud-storage",
            "aiohttp"
        ],
        env_vars={
            "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
            "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
            "TOPIC_ID": TOPIC_ID
        },
    ),
)
