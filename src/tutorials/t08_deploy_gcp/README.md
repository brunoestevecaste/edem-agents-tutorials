# Deploy ADK Agent to GCP

Deploy a simple ADK dice-rolling agent to Google Cloud in two ways:

- Cloud Run: a serverless container service that exposes the ADK API server over HTTPS.
- Vertex AI Agent Engine: a managed runtime built for deploying and invoking agents.

This tutorial is self-contained. The deployable agent lives in `roll_die/` and includes its own `requirements.txt`, which is the folder shape expected by `adk deploy`.

## Concepts

- `root_agent`: the ADK agent object that deployment commands discover.
- `adk deploy cloud_run`: builds and deploys the agent as a Cloud Run service.
- `adk deploy agent_engine`: packages and deploys the agent to Vertex AI Agent Engine.
- Vertex AI Gemini: the model provider used in this tutorial.

## Prerequisites

Install dependencies locally:

```bash
uv sync --extra adk
```

Copy the example environment file and fill in your GCP values:

```bash
cp .env.example .env
```

For this tutorial, set at least these values in `.env`:

```bash
MODEL_PROVIDER=vertex
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
VERTEX_MODEL=gemini-2.5-flash-lite
STAGING_BUCKET=gs://your-agent-staging-bucket
CLOUD_RUN_SERVICE_NAME=roll-die-agent
CLOUD_RUN_SERVICE_URL=https://your-cloud-run-service-url
AGENT_ENGINE_ID=projects/your-project-number/locations/us-central1/reasoningEngines/your-engine-id
```

Load `.env` into your current shell:

```bash
set -a
source .env
set +a
```

Authenticate with Google Cloud:

```bash
gcloud auth login
gcloud auth application-default login
```

Select your project:

```bash
gcloud config set project "$GOOGLE_CLOUD_PROJECT"
```

Enable the required APIs:

```bash
gcloud services enable \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

Create a staging bucket for Agent Engine:

```bash
gsutil mb -l "$GOOGLE_CLOUD_LOCATION" "$STAGING_BUCKET"
```

## Environment

All deployment commands below read values from `.env`. If you open a new terminal, reload it before running the commands:

```bash
set -a
source .env
set +a
```

The agent sets `GOOGLE_GENAI_USE_VERTEXAI=True` in code, so ADK uses Vertex AI instead of the Gemini API.

## Local Smoke Test

Run the agent locally before deploying:

```bash
uv run adk web src/tutorials/t08_deploy_gcp
```

Open [http://localhost:8000](http://localhost:8000), pick **roll_die**, and try:

- "Roll a 6-sided die 3 times"
- "Roll a 20-sided die"

## Deploy to Cloud Run

Deploy the agent with the ADK CLI:

```bash
uv run adk deploy cloud_run \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --service_name=roll-die-agent \
  --app_name=roll_die \
  --with_ui \
  src/tutorials/t08_deploy_gcp/roll_die
```

The command prints the Cloud Run service URL when deployment finishes. Open that URL in your browser to use the ADK web UI that was included with `--with_ui`.
Save the service URL in `.env` as `CLOUD_RUN_SERVICE_URL` if you want to call it from the notebook.

You can also fetch the URL later:

```bash
gcloud run services describe roll-die-agent \
  --region=$GOOGLE_CLOUD_LOCATION \
  --format='value(status.url)'
```

If you deploy without public access, authenticate requests with an identity token:

```bash
SERVICE_URL="$(gcloud run services describe roll-die-agent \
  --region=$GOOGLE_CLOUD_LOCATION \
  --format='value(status.url)')"

curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$SERVICE_URL"
```

## Deploy to Agent Engine

Deploy the same agent folder to Vertex AI Agent Engine:

```bash
uv run adk deploy agent_engine \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --staging_bucket=$STAGING_BUCKET \
  --display_name="roll-die-agent" \
  --trace_to_cloud \
  src/tutorials/t08_deploy_gcp/roll_die
```

The command prints the Agent Engine resource name. Save it:

```bash
# Add the value returned by the deploy command to .env, then reload it.
AGENT_ENGINE_ID=projects/<PROJECT_NUMBER>/locations/<REGION>/reasoningEngines/<ENGINE_ID>
```

Invoke it from Python:

```bash
uv run python - <<'PY'
import asyncio
import os

import vertexai
from vertexai import agent_engines

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    staging_bucket=os.environ["STAGING_BUCKET"],
)

remote_app = agent_engines.get(os.environ["AGENT_ENGINE_ID"])


async def main():
    remote_session = await remote_app.async_create_session(user_id="u_123")
    async for event in remote_app.async_stream_query(
        user_id="u_123",
        session_id=remote_session["id"],
        message="Roll a 6-sided die 3 times",
    ):
        print(event)


asyncio.run(main())
PY
```

Because the deploy command uses `--trace_to_cloud`, you can inspect traces in Google Cloud Trace Explorer.

## Notebook Client

After both deployments are available, call them from the notebook:

```bash
uv sync --extra adk --extra notebooks
uv run jupyter notebook notebooks/deploy_gcp_clients.ipynb
```

The notebook reads `.env`, creates an ADK session against Cloud Run, calls `/run`, and then calls the same deployed agent through `vertexai.agent_engines`.

## Cleanup

Delete the Cloud Run service:

```bash
gcloud run services delete roll-die-agent \
  --region=$GOOGLE_CLOUD_LOCATION
```

Delete the Agent Engine deployment from the Vertex AI console, or from Python:

```bash
uv run python - <<'PY'
import os

import vertexai
from vertexai import agent_engines

vertexai.init(
    project=os.environ["GOOGLE_CLOUD_PROJECT"],
    location=os.environ["GOOGLE_CLOUD_LOCATION"],
    staging_bucket=os.environ["STAGING_BUCKET"],
)

agent_engines.delete(os.environ["AGENT_ENGINE_ID"], force=True)
PY
```
