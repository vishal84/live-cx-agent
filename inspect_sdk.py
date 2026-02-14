import vertexai
from dotenv import load_dotenv
import os

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")

vertexai.init(project=PROJECT_ID, location=LOCATION)

try:
    from vertexai.preview import agent_engines
    print("Found vertexai.preview.agent_engines")
    print("Dir:", dir(agent_engines))
    if hasattr(agent_engines, "AgentEngine"):
        print("AgentEngine help:", help(agent_engines.AgentEngine))
    if hasattr(agent_engines, "create"):
        print("agent_engines.create help:", help(agent_engines.create))
except ImportError as e:
    print(f"Could not import vertexai.preview.agent_engines: {e}")

try:
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    if hasattr(client, "agent_engines"):
        print("client.agent_engines type:", type(client.agent_engines))
        print("client.agent_engines dir:", dir(client.agent_engines))
        if hasattr(client.agent_engines, "create"):
             print("client.agent_engines.create attributes:", client.agent_engines.create.__code__.co_varnames)
    else:
        print("client does not have agent_engines attribute")
except Exception as e:
    print(f"Error inspecting client: {e}")
