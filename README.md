# Live CX Agent

A sample ADK agent that demonstrates how to transfer a user to a live agent. This project is built using the Google Agent Development Kit (ADK).

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.12 or higher
*   `uv` (or `pip` and `venv`)

### Installation

1.  **Clone the repository:**

    ```sh
    git clone <repository-url>
    cd live-cx-agent
    ```

2.  **Install dependencies:**

    The project uses `pyproject.toml` to manage dependencies.

    Using `uv`:
    ```sh
    uv sync
    ```
    This will install the packages in editable mode. The dependencies are listed in `pyproject.toml`.

3.  **Configure environment variables:**

    Create a `.env` file by copying the example file:

    ```sh
    cp .env.example .env
    ```

    Open the `.env` file and fill in the required values. You will need to deploy the agent first to get an `AGENT_ENGINE_ID`, the script will automatically update the `.env` file with the `AGENT_ENGINE_ID` value. 
    
    You can do this by running:
    ```sh
    python deploy/deploy.py
    ```
    This will create the agent engine on Vertex AI and update your `.env` file with the `AGENT_ENGINE_ID`.

    ```sh
    python deploy/update.py
    ```
    After deploying run the update script as well so that the `AGENT_ENGINE_ID` environment variable gets
    populated properly.

## Running the Agent

To run the agent locally for development, you can use the ADK CLI. The following command will start a local server for your agent.

The main application object is `adk_app` located in `agent/agent.py`.

```sh
uv run adk web --reload_agents --session_service_uri <agent_engine_id>
```

**Arguments:**

*   `--reload_agents`: This flag enables hot-reloading, so the server will restart automatically when you make changes to your agent code.
*   `--session_service_uri <agent_engine_id>`: This connects your local agent to the session service of your deployed agent engine, allowing you to persist session history. Replace `<agent_engine_id>` with the ID you obtained during deployment (it should be in your `.env` file).

From the ADK Web UI you can run two tools:
* One to get the date and time
* The second to simulate a transfer to a live agent. This doesn't actually invoke a 3p CX agent but makes a long running API call that returns data and updates session in the background.

## Gemini Enterprise
Use Agent Registry to deploy the agent running on Agent Engine to Gemini Enterprise and test from a Gemini Enterprise frontend application.