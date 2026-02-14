import os
import logging
import vertexai
from dotenv import load_dotenv

# Load environment variables from the same directory as this file
load_dotenv()

GOOGLE_CLOUD_PROJECT=os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION=os.getenv("GOOGLE_CLOUD_LOCATION")


client = vertexai.Client(
  project=os.getenv(GOOGLE_CLOUD_PROJECT),
  location=os.getenv(GOOGLE_CLOUD_LOCATION)
)

# If you don't have an Agent Engine instance already, create an instance.
agent_engine = client.agent_engines.create(
  name="live-cx-agent",
  description="Agent Engine for live-cx-agent",
)

# Print the agent engine ID, you will need it in the later steps to initialize
# the ADK `VertexAiSessionService`.
print(agent_engine.api_resource.name.split("/")[-1])