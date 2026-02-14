import os
import logging
import vertexai
from dotenv import load_dotenv

# Load environment variables from the same directory as this file
load_dotenv()

GOOGLE_CLOUD_PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")

# Initialize Vertex AI SDK
vertexai.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)

client = vertexai.Client(
  project=GOOGLE_CLOUD_PROJECT,
  location=GOOGLE_CLOUD_LOCATION
)

# Import the adk_app AFTER environment variables are loaded and Vertex AI is initialized
from agent import adk_app

# If you don't have an Agent Engine instance already, create an instance.
agent_engine = client.agent_engines.create(
  agent=adk_app,
  config={
      "display_name": "live-cx-agent",      # Optional.
      "requirements": [
        "google-adk>=1.21.0",
        "python-dotenv>=1.0.0",
        "google-cloud-aiplatform[adk,agent_engines]",
        "google-cloud-vertexai"
    ],
    "staging_bucket": "gs://kpmg-agents-agent-engine",  # Required.
  },
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(agent_engine.api_resource.name.split("/")[-1])

