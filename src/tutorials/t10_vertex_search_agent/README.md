# Vertex AI Search Agent

A managed search tutorial: download a PDF from a URL, stage it in Google Cloud Storage, import it into a Vertex AI Search data store, then query it from an ADK agent using `VertexAiSearchTool`.

## Concepts

- Managed document search with Vertex AI Search (Discovery Engine)
- Async document import from GCS with the Discovery Engine Python client
- ADK's `VertexAiSearchTool` — model-native Gemini grounding (no explicit function call)
- Separating indexing time from agent runtime

## Contrast with t09 (Local RAG)

| | t09 Local RAG | t10 Vertex AI Search |
|---|---|---|
| Vector store | Local FAISS file | Managed by Google Cloud |
| Embedding | Explicit (LlamaIndex) | Handled by Vertex AI |
| Retrieval | `LlamaIndexRetrieval` (function call) | `VertexAiSearchTool` (model grounding) |
| Setup | Notebook only | Notebook + GCP data store |

## Setup

```bash
uv sync --extra adk --extra notebooks --extra rag
gcloud auth application-default login
```

Enable the required GCP APIs (one-time per project):

```bash
gcloud services enable \
  discoveryengine.googleapis.com \
  storage.googleapis.com \
  --project=YOUR_PROJECT_ID
```

Configure your project and a GCS staging bucket (reuse the same bucket from other tutorials):

```bash
export MODEL_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export VERTEX_RAG_STAGING_BUCKET="gs://your-staging-bucket"
# optional
export VERTEX_MODEL="gemini-2.5-flash-lite"
```

> **Model requirement**: `VertexAiSearchTool` uses Gemini's built-in grounding mechanism. It only
> works with Gemini models. `MODEL_PROVIDER=vertex` or `MODEL_PROVIDER=gemini` are both supported.

## 1. Build The Data Store

Choose a PDF URL. The notebook defaults to the Agencia Tributaria Renta 2025 manual:

```bash
export VERTEX_SEARCH_PDF_URL="https://sede.agenciatributaria.gob.es/..."
```

Run the notebook from the repository root:

```bash
uv run jupyter notebook notebooks/vertex_search_indexing.ipynb
```

The notebook downloads the PDF, uploads it to your GCS bucket, creates a Vertex AI Search data
store, and imports the PDF. It prints the full data store resource name — copy it into `.env`:

```bash
VERTEX_SEARCH_DATA_STORE_ID=projects/YOUR_PROJECT/locations/global/collections/default_collection/dataStores/agents-tutorials-search
```

## 2. Run The Agent

```bash
uv run adk web src/tutorials/t10_vertex_search_agent
```

Open [http://localhost:8000](http://localhost:8000), pick **vertex_search**, and try:

- "Qué novedades principales incluye el manual?"
- "Qué indica el manual sobre el mínimo personal y familiar?"
- "Resume lo que dice el PDF sobre rendimientos del trabajo"
- "Dónde aparece información sobre deducciones?"

## Notes

Vertex AI Search retrieval is model-native: the model fetches context from the data store
automatically when answering. You will not see an explicit tool-call step in the ADK trace.

The downloaded PDF is local and ignored by git. The data store and its index live in Google Cloud.
If you change the PDF or want to re-index, re-run `notebooks/vertex_search_indexing.ipynb`.
